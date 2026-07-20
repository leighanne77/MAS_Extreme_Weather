"""Bioregion classification — the SIR block that makes MAS portable (2026-07-17).

One typed block per site. `ecological_archetype` (resolved from the IUCN GET biome, the
global pivot) selects the payload's ecological profile; `structure` selects the
geometry block + 4_map__* HTML variant. A US site and an international site of the
SAME functional type resolve to the SAME ecological_archetype.

Single source of the crosswalk: standards/reference/bioregions.yaml
(the resolver + generator live in payload_factory.tools.bioregion).

Provenance discipline: GET biome is REQUIRED (present worldwide); EPA + USACE are
US-only; efg / un_elu.* / epa_l3_l4 carry "[INFERRED — verify]" inline when they
come from a spatial lookup; coordinates stay approximate by design.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from enums import EcologicalArchetype, RegulatoryGate, SiteStructure

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class IucnGet(BaseModel):
    """IUCN Global Ecosystem Typology — the global pivot. `biome` is required."""

    model_config = _FROZEN
    realm: str | None = None
    biome: str = Field(min_length=1)              # REQUIRED — the one global key
    efg: str | None = None                        # "[INFERRED — verify]" from spatial lookup


class UsEpa(BaseModel):
    """EPA/CEC Omernik ecoregion levels — US only (optional)."""

    model_config = _FROZEN
    l1: str | None = None
    l3: str | None = None                         # "[INFERRED — verify]" from L3 shapefile PIP
    l4: str | None = None


class UnElu(BaseModel):
    """UN SEEA / USGS-Esri Global Ecological Land Unit factors (per-point)."""

    model_config = _FROZEN
    bioclimate: str | None = None
    landcover: str | None = None
    landform: str | None = None
    lithology: str | None = None


class UsaceLayer(BaseModel):
    """USACE regulatory/permitting layer — US only. This is the §404 GATE, not the
    funding owner; the funding path lives at `BioregionClassification.money_path`."""

    model_config = _FROZEN
    regional_supplement: str | None = None
    hgm_class: str | None = None                  # HgmClass value or descriptive composite
    epa_l3_l4: str | None = None
    regulatory_hook: str | None = None


class MoneyPath(BaseModel):
    """Archetype-level funding path for the site's NbS/opportunities — NOT owned by
    USACE (funding can be USACE §404, state MAR, a local regulator, or none-yet).
    References EXISTING money_shelf vocabulary only (no invented funding);
    `regulatory_gate` names the determination that unlocks it, when one applies."""

    model_config = _FROZEN
    nbs_ids: list[str] = Field(default_factory=list)          # nature_based_solutions.json ids
    funding_sources: list[str] = Field(default_factory=list)  # funding_sources_NSB.json names (may be empty)
    credit_types: list[str] = Field(default_factory=list)     # RevenueStream.credit_type vocab
    regulatory_gate: RegulatoryGate = RegulatoryGate.NONE


class BioregionClassification(BaseModel):
    """SIR bioregion block — attaches to metadata_typology.bioregion_binding.
    Referenced by the payload (FROM_SIR), never re-stated."""

    model_config = _FROZEN

    block_type: str = Field(default="bioregion_classification", frozen=True)
    ecological_archetype: EcologicalArchetype            # REQUIRED — selects payload profile + HTML
    structure: SiteStructure | None = None        # selects geometry + 4_map__* variant
    iucn_get: IucnGet                             # REQUIRED (biome is the pivot key)
    us_epa: UsEpa | None = None                   # US only
    un_elu: UnElu | None = None
    usace: UsaceLayer | None = None               # US-only regulatory GATE
    money_path: MoneyPath | None = None           # funding — present US + international; not owned by USACE
    provenance_note: str = (
        "GET biome required (global pivot); EPA/USACE US-only; efg/elu/epa_l3_l4 "
        "'[INFERRED — verify]' when from spatial lookup; coordinates approximate by design."
    )

    @model_validator(mode="after")
    def _get_biome_is_the_pivot(self) -> "BioregionClassification":
        if not self.iucn_get or not self.iucn_get.biome:
            raise ValueError("iucn_get.biome is the required global pivot key (present on every site)")
        # USACE is US-only regulatory/funding — a bare USACE block without EPA is a smell, not an error.
        return self
