"""Knowledge-provider block — hyper-local, geolocated, bioregion-linked.

Two tracks in one ecosystem (per the ILK criteria + local scientific experts):
  ILK (practice-based): A1 tribal (CARE) · A2 nature-proximate · B citizen-science
  Scientific (formal):  S1 academic/field-station · S2 research institute · S3 consultant
Every provider carries COORDINATES (the user's requirement: geolocation linked)
and a bioregion/watershed binding, so relevance = proximity + shared bioregion,
not "the site generically" (cf. gauge-instance discipline E5).
"""
from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field, model_validator

from enums import CoordConfidence, ProviderClass

from payload_factory.models.blocks import Citation

_FROZEN = ConfigDict(frozen=True, extra="forbid")

_ILK = {ProviderClass.TRIBAL, ProviderClass.NATURE_PROXIMATE, ProviderClass.CITIZEN_SCIENCE}
_TIER_OK = {
    ProviderClass.TRIBAL: "A1", ProviderClass.NATURE_PROXIMATE: "A2",
    ProviderClass.CITIZEN_SCIENCE: "B", ProviderClass.ACADEMIC: "S1",
    ProviderClass.RESEARCH_INSTITUTE: "S2", ProviderClass.CONSULTING_SCIENTIST: "S3",
}


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 1)


class ProviderDataset(BaseModel):
    """An EXISTING published dataset from a knowledge provider — the collaboration hook."""

    model_config = _FROZEN

    name: str
    url: str | None = None
    url_absent_reason: str | None = None
    description: str | None = None
    access: str = "open"                       # open | request | exchange-sealed | unknown
    discovery_status: str = "found"            # found | swept-none | to-sweep

    @model_validator(mode="after")
    def _url_or_reason(self) -> "ProviderDataset":
        if self.url is None and not self.url_absent_reason and self.discovery_status == "found":
            raise ValueError(f"dataset '{self.name}': found datasets need a URL or url_absent_reason")
        return self


class KnowledgeProvider(BaseModel):
    """A geolocated local knowledge group — ILK holder or scientific expert."""

    model_config = _FROZEN

    name: str
    provider_class: ProviderClass
    tier: str                                  # A1/A2/B or S1/S2/S3
    institution: str | None = None
    lat: float
    lon: float
    coord_conf: CoordConfidence
    bioregion: str | None = None               # EPA ecoregion / bioregion binding
    watershed_huc: str | None = None
    domains: list[str] = Field(min_length=1)   # expertise domains
    consent_status: str                        # consent-first (tribal) | attribution | pending
    exchange_eligible: bool = False            # non-federal may be paid via Sealed Exchange
    citations: list[Citation] = Field(min_length=1)   # institution/dataset URLs — mandatory
    datasets: list[ProviderDataset] = Field(default_factory=list)   # existing published data (collaboration hook)
    collaboration_status: str = "prospect"     # prospect | discovery-pending | collaborating | declined

    @model_validator(mode="after")
    def _tier_matches_class(self) -> "KnowledgeProvider":
        if self.tier != _TIER_OK[self.provider_class]:
            raise ValueError(f"{self.name}: tier {self.tier} != class {self.provider_class.value} "
                             f"(expected {_TIER_OK[self.provider_class]})")
        if self.provider_class == ProviderClass.TRIBAL and "consent" not in self.consent_status.lower():
            raise ValueError(f"{self.name}: tribal (A1) provider requires consent-first status")
        return self

    def is_ilk(self) -> bool:
        return self.provider_class in _ILK


class KnowledgeProvidersBlock(BaseModel):
    """The hyper-local knowledge ecosystem for a site — both tracks, geolocated."""

    model_config = _FROZEN

    block_type: str = Field(default="knowledge_providers", frozen=True)
    site_id: str
    site_lat: float
    site_lon: float
    crs: str = "EPSG:4326"
    providers: list[KnowledgeProvider] = Field(min_length=1)

    def with_distances(self) -> list[dict]:
        """Providers annotated with km-to-site, nearest first (hyper-local ranking)."""
        rows = []
        for p in self.providers:
            rows.append(dict(
                name=p.name, cls=p.provider_class.value, tier=p.tier,
                institution=p.institution or "—", bioregion=p.bioregion or "—",
                domains=", ".join(p.domains), consent=p.consent_status,
                exchange="yes" if p.exchange_eligible else "no",
                km=haversine_km(self.site_lat, self.site_lon, p.lat, p.lon),
                lat=p.lat, lon=p.lon, coord_conf=p.coord_conf.value,
                datasets=len(p.datasets), collaboration=p.collaboration_status,
                url=(str(p.citations[0].url) if p.citations[0].url else None)))
        return sorted(rows, key=lambda r: r["km"])
