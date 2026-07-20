"""Block models for Briefs — every figure typed, cited, and traceable.

House rules encoded here (not in prose):
- A Figure cannot exist without at least one Citation ("no naked figures").
- A computed Figure must carry a CalcTrace ("no naked ROI").
- Citations carry a resolvable URL or an explicit absence reason.
- Gauge observations bind to a SPECIFIC station instance (decision E5);
  a gap is a status, never a zero (D-surge-3).
- Reserved multimodal/vintage fields (evidence_type, checksum, vintage)
  so v2 needs no breaking migration.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from enums import (
    DataProvenance,
    EvidenceType,
    FigureStatus,
    Grade,
    PreferenceClass,
    SourceContinuity,
)

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class Citation(BaseModel):
    """One source line behind a figure — popup/endnote-ready."""

    model_config = _FROZEN

    source: str = Field(min_length=1)
    publisher: str | None = None
    url: HttpUrl | None = None
    url_absent_reason: str | None = None
    accessed: date
    provenance: DataProvenance = DataProvenance.API
    evidence_type: EvidenceType = EvidenceType.SCALAR
    vintage: str | None = None            # e.g. "pre-2026 federal vintage 2025-12"
    archived_copy: HttpUrl | None = None  # escrow / Wayback / DataLumos pointer
    checksum: str | None = None           # escrow integrity (sha256:…)
    continuity: SourceContinuity = SourceContinuity.STABLE
    preference: PreferenceClass = PreferenceClass.P2_STANDARD
    note: str | None = None

    @model_validator(mode="after")
    def _url_or_reason(self) -> "Citation":
        if self.url is None and not self.url_absent_reason:
            raise ValueError(
                f"citation '{self.source}': url required, or url_absent_reason must say why"
            )
        return self


class CalcTrace(BaseModel):
    """Formula + named inputs behind a computed figure (eve:metricFormula)."""

    model_config = _FROZEN

    formula: str = Field(min_length=1)          # human-readable, e.g. "obs - predicted tide"
    inputs: dict[str, str] = Field(min_length=1)  # input name -> source/citation key
    method_note: str | None = None


class ModelRef(BaseModel):
    """Which downscaling/model produced a figure, and why it was routed."""

    model_config = _FROZEN

    model_name: str                              # e.g. "USGS CoSMoS"
    version: str | None = None
    scenario: str | None = None                  # e.g. "SSP2-4.5"
    ensemble_members: int | None = None
    routing_rule: str | None = None              # e.g. "coastal_flood@CA -> CoSMoS (routing v1)"
    validated_against: str | None = None         # observed anchor description
    grade: Grade = Grade.UNGRADED


class SensitivityEntry(BaseModel):
    """The same figure under an alternate model/member — 'impact of the model'."""

    model_config = _FROZEN

    alternative: str                             # e.g. "STAR-ESDM" / "obs-trend extrapolation"
    value: Decimal
    note: str | None = None


class Figure(BaseModel):
    """A number in a Brief. Typed, cited, status-tagged — or it doesn't exist."""

    model_config = _FROZEN

    label: str = Field(min_length=1)
    value: Decimal
    unit: str = Field(min_length=1)              # QUDT-aligned string; IRI via ontology_binding
    status: FigureStatus
    kind: str = Field(default="observed", pattern="^(observed|computed|projected)$")
    citations: list[Citation] = Field(min_length=1)
    calc_trace: CalcTrace | None = None
    model_ref: ModelRef | None = None
    sensitivity: list[SensitivityEntry] = Field(default_factory=list)
    grade: Grade = Grade.UNGRADED
    narrative: str | None = None                 # agent-draftable; never a number

    @model_validator(mode="after")
    def _traces_required(self) -> "Figure":
        if self.kind == "computed" and self.calc_trace is None:
            raise ValueError(f"figure '{self.label}': computed figures require calc_trace")
        if self.kind == "projected" and self.model_ref is None:
            raise ValueError(f"figure '{self.label}': projected figures require model_ref")
        return self


class GaugeStation(BaseModel):
    """A specific gauge instance — exposure and location are first-class (E5)."""

    model_config = _FROZEN

    station_id: str
    name: str
    exposure_role: str                            # "validation" | "asset-proximate" | "bay"
    lat: float
    lon: float
    record_start: date | None = None
    record_end: date | None = None                # None = active


class GaugeEventObservation(BaseModel):
    """One gauge x one event. A gap is a finding, never a zero (D-surge-3)."""

    model_config = _FROZEN

    station_id: str
    event: str
    status: FigureStatus                          # VERIFIED or REPORTED_NEGATIVE (no data)
    peak_storm_tide: Figure | None = None
    peak_residual: Figure | None = None
    no_data_reason: str | None = None

    @model_validator(mode="after")
    def _data_or_reason(self) -> "GaugeEventObservation":
        has_data = self.peak_storm_tide is not None or self.peak_residual is not None
        if self.status == FigureStatus.REPORTED_NEGATIVE:
            if has_data:
                raise ValueError(f"{self.station_id}/{self.event}: reported-negative cannot carry figures")
            if not self.no_data_reason:
                raise ValueError(f"{self.station_id}/{self.event}: reported-negative requires no_data_reason")
        elif not has_data:
            raise ValueError(f"{self.station_id}/{self.event}: needs figures or reported-negative status")
        return self


class HazardObsBlock(BaseModel):
    """Observed-hazard section block: stations + per-event observations."""

    model_config = _FROZEN

    block_type: str = Field(default="hazard_observations", frozen=True)
    hazard: str                                   # e.g. "coastal water level / storm surge"
    site_id: str                                  # e.g. "sr37-vallejo-ca"
    stations: list[GaugeStation] = Field(min_length=1)
    observations: list[GaugeEventObservation] = Field(min_length=1)
    method_caveat: str | None = None              # e.g. Delta-outflow residual caveat

    @model_validator(mode="after")
    def _obs_reference_known_stations(self) -> "HazardObsBlock":
        known = {s.station_id for s in self.stations}
        for o in self.observations:
            if o.station_id not in known:
                raise ValueError(f"observation references unknown station {o.station_id}")
        return self
