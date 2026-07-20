"""Local-economy VIP block — geolocated economic anchors (ADR-0022).

VIPs are the economic denominator of regional benefit: who the corridor protects
and by how much. A VIP qualifies as a LARGE EMPLOYER *or* a LARGE TAXPAYER (the
latter may have few employees — data center, mine, refinery). Geolocation is
required (relevance = proximity + who a closure severs). Economic magnitudes are
CITED (CBP/QCEW/LEHD/assessor) or TO_BE_FILLED — never invented.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from datetime import date

from enums import CoordConfidence, OperatingStatus
from payload_factory.models.blocks import Citation, Figure
from payload_factory.models.knowledge import haversine_km

_FROZEN = ConfigDict(frozen=True, extra="forbid")
_CRITERIA = {"large_employer", "large_taxpayer", "both"}


class LocalEconomyVIP(BaseModel):
    """A geolocated large employer and/or large taxpayer."""

    model_config = _FROZEN

    name: str
    sector: str                                 # motorsports, refinery, winery, data-center, shipyard, mine, hospital...
    qualifying_criterion: str                   # large_employer | large_taxpayer | both
    lat: float
    lon: float
    coord_conf: CoordConfidence
    employees: Figure | None = None             # cited or TO_BE_FILLED
    tax_or_revenue: Figure | None = None        # the large-taxpayer magnitude (cited or TBF)
    why_matters: str                            # relevance to the corridor / region
    operating_status: OperatingStatus           # REQUIRED liveness (ground-truthed)
    status_as_of: date | None = None            # when liveness was last checked
    status_basis: str = "verify"                # what confirmed it (news/financials) — or 'verify'
    citations: list[Citation] = Field(min_length=1)

    def is_benefit_anchor(self) -> bool:
        """Only an ACTIVE entity counts as a benefit to protect; others are context/loss."""
        return self.operating_status == OperatingStatus.ACTIVE

    @model_validator(mode="after")
    def _criterion_valid(self) -> "LocalEconomyVIP":
        if self.qualifying_criterion not in _CRITERIA:
            raise ValueError(f"{self.name}: qualifying_criterion must be one of {_CRITERIA}")
        return self


class LocalEconomyVIPBlock(BaseModel):
    """Required geolocated set of local-economy VIPs for a site."""

    model_config = _FROZEN

    block_type: str = Field(default="local_economy_vips", frozen=True)
    site_id: str
    site_lat: float
    site_lon: float
    crs: str = "EPSG:4326"
    vips: list[LocalEconomyVIP] = Field(min_length=1)   # REQUIRED (>=1, or reported-negative upstream)

    def with_distances(self) -> list[dict]:
        rows = []
        for v in self.vips:
            rows.append(dict(
                name=v.name, sector=v.sector, criterion=v.qualifying_criterion,
                status=v.operating_status.value, status_basis=v.status_basis,
                anchor=v.is_benefit_anchor(),
                employees=(str(v.employees.value) if v.employees else "TBF"),
                tax_or_revenue=(str(v.tax_or_revenue.value) if v.tax_or_revenue else "TBF"),
                why=v.why_matters, coord_conf=v.coord_conf.value,
                km=haversine_km(self.site_lat, self.site_lon, v.lat, v.lon),
                url=(str(v.citations[0].url) if v.citations[0].url else None)))
        return sorted(rows, key=lambda r: r["km"])
