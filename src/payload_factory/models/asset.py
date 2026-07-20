"""Asset block — the single-asset geometry (structure = single-asset).

The structure-level analog of SegmentationBlock (corridor): a point-asset
(shipyard · port · terminal · coastal facility) cut into ZONES instead of a
corridor into segments. STRUCTURE-level, NOT archetype-level — a coastal or an
arid single-asset both use this block; only the CONTENT (hazards, ecology,
NbS / money_path) differs by ecological_archetype. Mirrors models/corridor.py.
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from enums import ClaimTag, CoordConfidence

from payload_factory.models.blocks import Citation

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class AssetZone(BaseModel):
    """One facility sub-area — the map / vulnerability unit (single-asset analog
    of CorridorSegment). Coordinates carry CoordConfidence (approximate by design)."""

    model_config = _FROZEN

    zone_id: str
    name: str
    lat: float
    lon: float
    coord_conf: CoordConfidence
    claim: ClaimTag = ClaimTag.KNOWN
    exposure: str | None = None          # what this zone is exposed to
    color: str | None = None             # #hex for the map render
    notes: str | None = None


class AssetBlock(BaseModel):
    """A coastal/other point-asset cut into typed zones (Coastal-Single-Asset ENI §asset)."""

    model_config = _FROZEN

    block_type: str = Field(default="asset", frozen=True)
    site_id: str
    asset_name: str
    typology: list[str] = Field(min_length=1)      # e.g. ["shipyard", "coastal point-asset"]
    waterbody: str | None = None
    lat: float
    lon: float
    coord_conf: CoordConfidence
    acreage: Decimal | None = None
    owner_operator: str | None = None
    zones: list[AssetZone] = Field(min_length=1)
    citations: list[Citation] = Field(min_length=1)   # geometry/source basis
    note: str | None = None

    @model_validator(mode="after")
    def _unique_zone_ids(self) -> "AssetBlock":
        ids = [z.zone_id for z in self.zones]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate zone_id in asset block")
        return self
