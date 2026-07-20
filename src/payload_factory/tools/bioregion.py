"""Bioregion resolver + crosswalk generator (2026-07-17).

Reuses the registered binding engine (bioregions.yaml + geography_parser) — it does
NOT fork it (reuse-first; ADR-0024). Two responsibilities:

  build_crosswalk() / write_crosswalk_json()
      GENERATE the machine-readable src/data/bioregion_crosswalk.json from the
      single source standards/reference/bioregions.yaml. Never hand-edit the JSON;
      tests/test_bioregion_crosswalk.py drift-tests it against a fresh regen.

  resolve_bioregion(lat, lon, country, state?, county?)
      -> BioregionClassification. IUCN GET biome is the pivot: biome -> ecological_archetype.
      US sites add EPA + USACE; international sites are GET-only. Spatially-derived
      fields (efg, EPA L3/L4, ELU) are tagged "[INFERRED — verify]".

ENVIRONMENT NOTE: geopandas/rasterio/fiona are not installed and no ecoregion
shapefiles / GET layer / ELU raster / USACE geodatabase ship with the repo, so true
point-in-polygon / raster sampling cannot run here. The spatial-layer hooks below are
defined and degrade to None (logging what to wire) — the working offline path is the
curated worked-bindings + the crosswalk table. It does NOT fake PIP on absent data.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml

from enums import EcologicalArchetype, SiteStructure  # noqa: F401  (validated by the model)
from payload_factory.models import BioregionClassification

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[3]                       # repo root
_YAML = _ROOT / "standards" / "reference" / "bioregions.yaml"
_JSON = Path(__file__).resolve().parents[2] / "data" / "bioregion_crosswalk.json"  # src/data/…
_LAYER_DIR = _ROOT / "data" / "curated" / "bioregions"            # where spatial layers land when wired

_INFERRED = "[INFERRED — verify]"
_TBF = "[TO_BE_FILLED]"

# Where each spatial layer comes from, surfaced when the layer file is absent.
_LAYER_SOURCES = {
    "epa_l3l4": "EPA Ecoregions L3/L4 shapefile — epa.gov/eco-research/ecoregions",
    "iucn_get": "IUCN GET spatial layer — iucnrle.org/global-eco-typo (global-ecosystems.org)",
    "un_elu": "USGS/Esri Global Ecological Land Units raster — SEEA",
    "usace": "USACE Regional Supplements + Subregions geodatabase — geospatial-usace.opendata.arcgis.com",
}


# ─────────────────────────────── generator (yaml -> json) ───────────────────────────────
def build_crosswalk(source_yaml: Path | None = None) -> dict:
    """Flatten bioregions.yaml into the machine-readable crosswalk the resolver reads.
    Deterministic (no wall-clock / ordering surprises) so it is drift-testable."""
    d = yaml.safe_load((source_yaml or _YAML).read_text())
    archetypes = {row["ecological_archetype"]: {k: v for k, v in row.items() if k != "ecological_archetype"}
                  for row in d.get("archetypes", [])}
    biome_to_archetype: dict[str, str] = {}
    for name, row in archetypes.items():
        for b in row.get("iucn_get", {}).get("biomes", []):
            biome_to_archetype.setdefault(b["code"], name)      # first archetype wins (stable)
    return {
        "_schema": "MAS bioregion crosswalk — GENERATED from standards/reference/bioregions.yaml. DO NOT hand-edit.",
        "_source": "standards/reference/bioregions.yaml",
        "frameworks": d.get("crosswalk_frameworks", {}),
        "resolution_logic": d.get("crosswalk_resolution_logic", {}),
        "structures": d.get("structures", {}),
        "archetypes": archetypes,
        "biome_to_archetype": biome_to_archetype,
    }


def _serialize(crosswalk: dict) -> str:
    return json.dumps(crosswalk, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_crosswalk_json(dest: Path | None = None) -> Path:
    dest = dest or _JSON
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_serialize(build_crosswalk()))
    return dest


def load_crosswalk() -> dict:
    """Read the generated JSON; fall back to building from the yaml if it is absent."""
    if _JSON.exists():
        return json.loads(_JSON.read_text())
    logger.info("bioregion_crosswalk.json not generated yet — building from bioregions.yaml in-memory")
    return build_crosswalk()


# ─────────────────────────── spatial-layer hooks (degrade honestly) ───────────────────────────
def _layer(name: str) -> Path | None:
    p = _LAYER_DIR / name
    if p.exists():
        return p
    logger.debug("bioregion layer %s absent — offline crosswalk path used. Wire: %s",
                 name, _LAYER_SOURCES.get(name.split(".")[0], name))
    return None


def _get_biome_at(lat: float, lon: float) -> str | None:
    """IUCN GET biome by point. Returns None until the GET layer is wired (see _LAYER_SOURCES)."""
    return None if _layer("iucn_get.geojson") is None else None  # PIP with shapely once the layer lands


def _epa_pip(lat: float, lon: float) -> tuple[str | None, str | None]:
    """EPA L3/L4 by point-in-polygon. None until the L3/L4 shapefile is wired."""
    _layer("epa_l3l4.geojson")
    return None, None


def _elu_sample(lat: float, lon: float) -> dict | None:
    """Sample the ELU raster's 4 factors at the point. None until the raster is wired."""
    return None if _layer("global_elu.tif") is None else None


def _usace_supplement(lat: float, lon: float) -> str | None:
    """USACE Regional Supplement by point. None until the supplements geodatabase is wired."""
    return None if _layer("usace_supplements.geojson") is None else None


# ─────────────────────────────── resolver ───────────────────────────────
def _worked_binding_match(lat: float, lon: float, tol: float = 0.6) -> dict | None:
    """A curated worked-binding whose centroid is within `tol` degrees — the
    highest-confidence offline path (these bindings are human-verified)."""
    d = yaml.safe_load(_YAML.read_text())
    for wb in d.get("worked_bindings", []):
        c = wb.get("centroid")
        bc = wb.get("bioregion_classification")
        if c and bc and abs(c["lat"] - lat) <= tol and abs(c["lon"] - lon) <= tol:
            return bc
    return None


def classification_for_site(site_id: str) -> BioregionClassification | None:
    """FROM_SIR accessor — the payload REFERENCES this, never re-states it
    (MAS_Two_Inventories single-source rule). Returns the curated worked-binding
    classification for a registered site, or None if the site has no binding yet."""
    d = yaml.safe_load(_YAML.read_text())
    for wb in d.get("worked_bindings", []):
        if wb.get("site") == site_id and wb.get("bioregion_classification"):
            return BioregionClassification.model_validate(wb["bioregion_classification"])
    return None


def _archetype_from_hints(country: str, state: str | None, county: str | None,
                          location_hint: str | None) -> tuple[str, str]:
    """Coarse offline archetype guess when there is no biome and no worked binding.
    Reuses geography_parser's location-type heuristic. Always tagged INFERRED."""
    from multi_agent_system.utils.geography_parser import parse_location
    loc = ", ".join(p for p in (location_hint, county, state, country) if p)
    ctx = parse_location(loc)
    lt = ctx.location_type
    if lt == "coastal":
        return "coastal-estuarine", f"location-type coastal ({loc}) {_INFERRED}"
    if lt == "riverine":
        return "riverine-inland-waterway", f"location-type riverine ({loc}) {_INFERRED}"
    if lt == "agricultural":
        return "great-plains", f"location-type agricultural ({loc}) {_INFERRED}"
    # last resort — do not fabricate; return riverine-inland-waterway as the most generic inland bucket
    return "riverine-inland-waterway", f"no biome/binding/location-type; generic inland fallback ({loc}) {_INFERRED}"


def resolve_bioregion(lat: float, lon: float, country: str,
                      state: str | None = None, county: str | None = None,
                      *, get_biome: str | None = None, structure: str | None = None,
                      location_hint: str | None = None) -> BioregionClassification:
    """Resolve a point to a BioregionClassification. GET biome is the pivot.

    country: ISO-ish country ("US" / "USA" / other). US sites get EPA + USACE.
    get_biome: an IUCN GET biome code (e.g. "MFT1"); when the GET spatial layer is
        wired, _get_biome_at fills this. Passing it drives the pivot directly.
    structure: single-asset | corridor | group (optional; selects geometry + HTML).
    """
    xw = load_crosswalk()
    archetypes = xw["archetypes"]
    is_us = country.strip().lower() in {"us", "usa", "u.s.", "united states"}

    # 1) highest confidence: a curated worked binding near this point
    wb = _worked_binding_match(lat, lon)
    if wb is not None:
        data = dict(wb)
        if structure and "structure" not in data:
            data["structure"] = structure
        return BioregionClassification.model_validate(data)

    # 2) GET pivot: biome (given, or from the GET layer) -> archetype
    biome_code = get_biome or _get_biome_at(lat, lon)
    if biome_code:
        arch_name = xw["biome_to_archetype"].get(biome_code.split()[0].split("—")[0].strip())
        basis = f"IUCN GET biome {biome_code} (pivot)"
    else:
        arch_name = None
        basis = None

    # 3) offline fallback: coarse hint-based archetype (INFERRED)
    if not arch_name:
        arch_name, basis = _archetype_from_hints(country, state, county, location_hint)

    row = archetypes[arch_name]

    # IUCN GET block — biome is the required pivot key
    get = row.get("iucn_get", {})
    first_biome = (get.get("biomes") or [{}])[0]
    biome_str = biome_code or f"{first_biome.get('code','')} — {first_biome.get('name','')}".strip(" —")
    first_efg = (get.get("representative_efgs") or [{}])[0]
    iucn = {"realm": (get.get("realms") or [None])[0], "biome": biome_str,
            "efg": (f"{first_efg.get('code','')} — {first_efg.get('name','')} {_INFERRED}".strip()
                    if first_efg else None)}

    # UN ELU — per-point in principle; offline we echo the archetype defaults, tagged INFERRED
    elu_src = _elu_sample(lat, lon) or row.get("un_elu", {})
    un_elu = {k: (f"{elu_src.get(k)} {_INFERRED}" if elu_src.get(k) else None)
              for k in ("bioclimate", "landcover", "landform", "lithology")}

    us_epa = usace = None
    if is_us:
        l3_pip, l4_pip = _epa_pip(lat, lon)
        us_epa = {"l1": (row.get("us_epa_l1") or [None])[0],
                  "l3": l3_pip or _TBF + " " + _INFERRED, "l4": l4_pip or _TBF}
        u = row.get("usace", {})   # US-only regulatory GATE (no funding here)
        usace = {"regional_supplement": _usace_supplement(lat, lon) or u.get("regional_supplement"),
                 "hgm_class": u.get("hgm_class"),
                 "epa_l3_l4": (u.get("epa_l3_examples") or [None])[0] and
                              f"{(u.get('epa_l3_examples') or [''])[0]} {_INFERRED}",
                 "regulatory_hook": u.get("regulatory_hook")}

    # money_path — funding is archetype-level and present US + international (NOT owned by USACE).
    money_path = dict(row.get("money_path") or {})
    if money_path and not is_us:
        # international: USACE §404 doesn't apply — a local regulator gates it; drop US-federal funding names
        money_path = {**money_path, "regulatory_gate": "local_regulator", "funding_sources": []}

    return BioregionClassification.model_validate({
        "ecological_archetype": arch_name,
        "structure": structure,
        "iucn_get": iucn,
        "us_epa": us_epa,
        "un_elu": un_elu,
        "usace": usace,
        "money_path": money_path or None,
        "provenance_note": f"archetype basis: {basis}. " + BioregionClassification.model_fields["provenance_note"].default,
    })


if __name__ == "__main__":       # regenerate the JSON: python -m payload_factory.tools.bioregion
    p = write_crosswalk_json()
    print(f"wrote {p} ({len(build_crosswalk()['archetypes'])} archetypes)")
