"""Bioregion crosswalk integrity + drift (2026-07-17).

Guards the reconciliation invariants: GET biome is the required global pivot,
every archetype money_path references REAL money_shelf ids (no invented funding),
and src/data/bioregion_crosswalk.json is a faithful, unedited derive of
standards/reference/bioregions.yaml.
"""
import json
from pathlib import Path

import yaml

from payload_factory.tools.bioregion import build_crosswalk, _serialize, _JSON

ROOT = Path(__file__).resolve().parents[1]
YAML_SRC = ROOT / "standards" / "reference" / "bioregions.yaml"


def _real_nbs_ids() -> set[str]:
    d = json.loads((ROOT / "src/multi_agent_system/data/nature_based_solutions.json").read_text())
    return {s["id"] for s in d.get("solutions", []) if isinstance(s, dict) and s.get("id")}


def _real_funding_names() -> set[str]:
    txt = (ROOT / "src/multi_agent_system/data/funding_sources_NSB.json").read_text()
    d = json.loads(txt)
    names: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("name"), str):
                names.add(o["name"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(d)
    return names


# credit_type vocab documented on payload_factory.models.money.RevenueStream
_CREDIT_TYPES = {"biodiversity", "wetland-mitigation-bank", "species-conservation-bank",
                 "water-quality-trading", "tidal-wetland", "stormwater"}


def test_generated_json_matches_source_yaml():
    """DRIFT: the committed JSON must equal a fresh regen (never hand-edited)."""
    assert _JSON.exists(), "run: .venv/bin/python -m payload_factory.tools.bioregion"
    assert _JSON.read_text() == _serialize(build_crosswalk()), \
        "src/data/bioregion_crosswalk.json drifted from bioregions.yaml — regenerate it"


def test_every_archetype_has_a_get_biome_pivot():
    xw = build_crosswalk()
    assert len(xw["archetypes"]) == 6
    for name, row in xw["archetypes"].items():
        biomes = row.get("iucn_get", {}).get("biomes", [])
        assert biomes and biomes[0].get("code"), f"{name}: GET biome is the required pivot key"


def test_biome_index_maps_the_pivot():
    xw = build_crosswalk()
    assert xw["biome_to_archetype"].get("MFT1") == "coastal-estuarine"
    assert xw["biome_to_archetype"].get("T5") == "arid-desert"


def test_money_path_references_real_money_shelf_ids():
    """The guardrail: the archetype-level money_path (NOT owned by USACE) must map to
    an EXISTING money_shelf path, and its regulatory_gate must be a valid enum value."""
    from enums import RegulatoryGate
    gates = {g.value for g in RegulatoryGate}
    xw = build_crosswalk()
    nbs, funding = _real_nbs_ids(), _real_funding_names()
    for name, row in xw["archetypes"].items():
        mp = row.get("money_path")
        assert mp, f"{name}: money_path required (funding-path guardrail)"
        assert mp.get("regulatory_gate") in gates, f"{name}: regulatory_gate {mp.get('regulatory_gate')!r} not in RegulatoryGate"
        for i in mp.get("nbs_ids", []):
            assert i in nbs, f"{name}: nbs id {i!r} not in nature_based_solutions.json (no invented funding)"
        for c in mp.get("credit_types", []):
            assert c in _CREDIT_TYPES, f"{name}: credit_type {c!r} not in RevenueStream vocab"
        for fs in mp.get("funding_sources", []):   # list now (may be empty); every named source must be real
            assert fs in funding, f"{name}: funding_source {fs!r} not in funding_sources_NSB.json"


def test_structures_axis_preserves_single_asset():
    xw = build_crosswalk()
    s = xw["structures"]
    assert set(s) == {"single-asset", "corridor", "group"}
    assert s["single-asset"]["payload_template"] == "coastal_single_asset_payload_TEMPLATE"


def test_sr37_worked_binding_is_a_valid_classification():
    from payload_factory.models import BioregionClassification
    d = yaml.safe_load(YAML_SRC.read_text())
    wb = next(w for w in d["worked_bindings"] if w["site"] == "sr37-vallejo-ca")
    bc = BioregionClassification.model_validate(wb["bioregion_classification"])
    assert bc.ecological_archetype.value == "coastal-estuarine"
    assert bc.iucn_get.biome.startswith("MFT1")
    assert bc.usace.regulatory_hook                          # USACE = regulatory gate only (no money_path attr)
    assert "USACE Beneficial Use Program" in bc.money_path.funding_sources
    assert bc.money_path.regulatory_gate.value == "usace_404_budm"
