"""Corridor blocks — segmentation, closure history, demand/anchor discipline.

House rules encoded:
- Typology varies BY SEGMENT (the corridor Standard's core mechanism).
- Coordinates carry CoordConfidence (site-of-sites legend: approximations,
  confidence-tagged, verify against survey-grade sources before use of record).
- Only OBLIGATED demand counts as anchor demand — a hypothetical or merely
  authorized/appropriated anchor CANNOT be marked counts_as_anchor.
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from enums import ClaimTag, CoordConfidence, DemandStatus

from payload_factory.models.blocks import Citation, Figure

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class CorridorSegment(BaseModel):
    """One segment of a linear corridor — typology is per-segment."""

    model_config = _FROZEN

    segment_id: str
    name: str
    typology: list[str] = Field(min_length=1)   # e.g. ["rural-coastal", "baylands"]
    lat: float
    lon: float
    coord_conf: CoordConfidence
    claim: ClaimTag = ClaimTag.KNOWN
    length_mi: Decimal | None = None
    elevation_note: str | None = None
    structures: list[str] = Field(default_factory=list)  # NBI structure ids
    notes: str | None = None


class SegmentationBlock(BaseModel):
    """The corridor cut into typed segments (Coastal Corridor Standard §0)."""

    model_config = _FROZEN

    block_type: str = Field(default="corridor_segmentation", frozen=True)
    site_id: str
    corridor_name: str
    termini: str
    total_length_mi: Decimal
    segments: list[CorridorSegment] = Field(min_length=1)
    citations: list[Citation] = Field(min_length=1)   # geometry/source basis
    note: str | None = None

    @model_validator(mode="after")
    def _unique_segment_ids(self) -> "SegmentationBlock":
        ids = [s.segment_id for s in self.segments]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate segment_id in segmentation block")
        return self


class ClosureEvent(BaseModel):
    """One documented closure/flooding event on the corridor."""

    model_config = _FROZEN

    event: str
    window: str                      # e.g. "2017-01-06 – 2017-02-21"
    cause: str
    days_closed: Figure | None = None   # Figure ⇒ citations enforced
    note: str | None = None

    @model_validator(mode="after")
    def _unfilled_needs_note(self) -> "ClosureEvent":
        if self.days_closed is None and not self.note:
            raise ValueError(f"{self.event}: no days_closed figure — note required (TO_BE_FILLED + source)")
        return self


class ClosureHistoryBlock(BaseModel):
    model_config = _FROZEN

    block_type: str = Field(default="closure_history", frozen=True)
    site_id: str
    events: list[ClosureEvent] = Field(min_length=1)
    citations: list[Citation] = Field(min_length=1)   # the log source(s)


class DemandAnchor(BaseModel):
    """A demand signal near the corridor. ONLY OBLIGATED counts as anchor."""

    model_config = _FROZEN

    name: str
    status: DemandStatus
    description: str = Field(min_length=1)
    counts_as_anchor: bool = False
    citations: list[Citation] = Field(min_length=1)

    @model_validator(mode="after")
    def _obligated_only(self) -> "DemandAnchor":
        if self.counts_as_anchor and self.status != DemandStatus.OBLIGATED:
            raise ValueError(
                f"anchor '{self.name}': counts_as_anchor requires status=obligated "
                f"(got {self.status.value}) — auth/appropriated/hypothetical are context, not anchors"
            )
        return self


class DemandBlock(BaseModel):
    model_config = _FROZEN

    block_type: str = Field(default="demand_anchors", frozen=True)
    site_id: str
    anchors: list[DemandAnchor] = Field(min_length=1)
    discipline_note: str = (
        "Per house discipline, only OBLIGATED funding counts as anchor demand; "
        "program mentions are context, not anchors."
    )


class StructurePoint(BaseModel):
    """An NBI structure as a located feature — survey-grade coordinates."""

    model_config = _FROZEN

    structure_id: str
    crosses: str
    year_built: int
    condition: str                    # "deck/super/sub" e.g. "5/7/5" ("N" = culvert/not rated)
    length_m: Decimal
    lat: float
    lon: float
    coord_conf: CoordConfidence = CoordConfidence.HIGH   # NBI is the authority's own record
    segment_id: str | None = None


class StructuresBlock(BaseModel):
    """Corridor structures inventory (NBI), located and condition-rated."""

    model_config = _FROZEN

    block_type: str = Field(default="corridor_structures", frozen=True)
    site_id: str
    crs: str = "EPSG:4326"
    structures: list[StructurePoint] = Field(min_length=1)
    citations: list[Citation] = Field(min_length=1)
