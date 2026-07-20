"""The two payload axes — ecological (the PLACE) × structure (the THING).

A payload is stamped from three inputs: a Site Inventory Record (facts) + one
ecological archetype + one structure archetype (see stamp.py). This module exposes
what standards/reference/bioregions.yaml already holds — via the generated crosswalk
(the single source) — as two typed selectors. Pure reads; no new taxonomy.

  axes.ecological(archetype) -> EcologicalProfile   # hazard signature, NbS/money menu, ecology, crosswalk
  axes.structure(structure)  -> StructureSpec       # geometry-block shape + which Map template
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from enums import EcologicalArchetype, SiteStructure
from payload_factory.models import AssetBlock, SegmentationBlock
from payload_factory.tools.bioregion import load_crosswalk

_FROZEN = ConfigDict(frozen=True, extra="forbid")

# structure axis -> the typed geometry block that carries its shape (group: TBD)
_GEOMETRY: dict[SiteStructure, type | None] = {
    SiteStructure.SINGLE_ASSET: AssetBlock,       # asset { footprint, zones[] }
    SiteStructure.CORRIDOR: SegmentationBlock,    # corridor { termini, segments[] }
    SiteStructure.GROUP: None,                    # site-of-sites — TO_BE_DEFINED
}


class EcologicalProfile(BaseModel):
    """The PLACE — resolved from axes.ecological[archetype] (bioregions.yaml archetypes[])."""

    model_config = _FROZEN

    archetype: EcologicalArchetype
    hazard_signature: list[str] = Field(default_factory=list)
    money_path: dict = Field(default_factory=dict)   # nbs_ids / funding_sources / credit_types / regulatory_gate
    iucn_get: dict = Field(default_factory=dict)      # realms / biomes / representative_efgs
    us_epa_l1: list[str] = Field(default_factory=list)
    un_elu: dict = Field(default_factory=dict)
    usace: dict = Field(default_factory=dict)         # regulatory gate (US)
    us_examples: list[str] = Field(default_factory=list)
    international_analog: str | None = None


class StructureSpec(BaseModel):
    """The THING — resolved from axes.structure[structure] (bioregions.yaml structures{})."""

    model_config = _FROZEN

    structure: SiteStructure
    geometry_block: str            # geometry model class name: "AssetBlock" | "SegmentationBlock" | "TO_BE_DEFINED"
    html_map: str = ""             # which 4_map__* render this structure drives
    value_model: str | None = None  # ebitda_at_risk (single-asset) | closure_days_bcr (corridor) | ...


def ecological(archetype: EcologicalArchetype | str) -> EcologicalProfile:
    """The ecological axis — one archetype -> its PLACE profile."""
    a = EcologicalArchetype(archetype)
    row = load_crosswalk()["archetypes"].get(a.value)
    if row is None:
        raise KeyError(f"axes.ecological: no profile for archetype {a.value!r}")
    return EcologicalProfile(
        archetype=a,
        hazard_signature=row.get("hazard_signature", []),
        money_path=row.get("money_path", {}),
        iucn_get=row.get("iucn_get", {}),
        us_epa_l1=row.get("us_epa_l1", []),
        un_elu=row.get("un_elu", {}),
        usace=row.get("usace", {}),
        us_examples=row.get("us_examples", []),
        international_analog=row.get("international_analog"),
    )


def structure(struct: SiteStructure | str) -> StructureSpec:
    """The structure axis — one structure -> its geometry-block + Map template."""
    s = SiteStructure(struct)
    spec = load_crosswalk()["structures"].get(s.value)
    if spec is None:
        raise KeyError(f"axes.structure: no spec for structure {s.value!r}")
    geom = _GEOMETRY.get(s)
    return StructureSpec(
        structure=s,
        geometry_block=(geom.__name__ if geom else "TO_BE_DEFINED"),
        html_map=spec.get("html_map", ""),
        value_model=spec.get("value_model"),
    )


def geometry_block_class(struct: SiteStructure | str) -> type | None:
    """The pydantic geometry model for a structure (AssetBlock / SegmentationBlock / None)."""
    return _GEOMETRY.get(SiteStructure(struct))
