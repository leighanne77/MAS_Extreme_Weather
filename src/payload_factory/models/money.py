"""Money Shelf — the investor's capital + revenue decision surface (ADR-0017).

Two sides:
  capital_sources  — how the build is FUNDED (grants, tax credits, concessional
                     debt, OZ). Concessionary types lower the cost of capital.
  revenue_streams  — what nature-positive mitigation EARNS BACK (biodiversity,
                     wetland/species mitigation banking, water-quality trading,
                     tidal-wetland credits). BIOREGION-SCOPED: mitigation-bank
                     service areas are watersheds; a FRESH list is generated per
                     bioregion in the briefing structure (standing registry).
Sibling of the Trophy Shelf (awards). NO insurance sources (eve-no-insurance).
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from payload_factory.models.blocks import Citation

_FROZEN = ConfigDict(frozen=True, extra="forbid")

# capital types, most-concessionary first (drives the cost-of-capital sort)
_CAPITAL_TYPES = {"grant", "tax-credit", "forgivable", "concessional-debt",
                  "guarantee", "below-market-debt", "market-debt", "equity"}
_CONCESSIONARY = {"grant", "tax-credit", "forgivable", "concessional-debt",
                  "guarantee", "below-market-debt"}


class CapitalSource(BaseModel):
    """A funding source (funding_sources_NSB.json), classed by cost of capital."""

    model_config = _FROZEN

    name: str
    category: str                              # Federal | State/Local | Private | Manufacturing | OZ
    capital_type: str                          # one of _CAPITAL_TYPES
    concessionary: bool = False
    discount_note: str | None = None           # e.g. "NMTC ~20% subsidy"; "grant = 100% non-dilutive"
    eligible_uses: list[str] = Field(default_factory=list)
    timeline: str | None = None
    citations: list[Citation] = Field(min_length=1)

    @model_validator(mode="after")
    def _valid(self) -> "CapitalSource":
        if self.capital_type not in _CAPITAL_TYPES:
            raise ValueError(f"{self.name}: capital_type {self.capital_type!r} not in {_CAPITAL_TYPES}")
        if self.concessionary != (self.capital_type in _CONCESSIONARY):
            raise ValueError(f"{self.name}: concessionary flag disagrees with capital_type {self.capital_type}")
        if "insurance" in self.name.lower() or "insurance" in self.category.lower():
            raise ValueError(f"{self.name}: insurance sources are excluded (eve-no-insurance)")
        return self


class RevenueStream(BaseModel):
    """An ecological-credit / revenue stream — BIOREGION-SCOPED."""

    model_config = _FROZEN

    name: str
    credit_type: str                           # biodiversity | wetland-mitigation-bank | species-conservation-bank | water-quality-trading | tidal-wetland | stormwater
    bioregion_scope: str = Field(min_length=1)  # the bioregion/watershed this market serves
    market_status: str                         # active | emerging | pilot | verify
    revenue_basis: str | None = None           # e.g. "$/wetland credit (acre)"; "$/species credit"
    operating_model: str | None = None         # sell-then-restore vs restore-then-sell; release schedule
    access: str = "verify"
    vocab_note: str | None = None              # terms-discipline flags (e.g. avoid 'carbon credit' framing)
    citations: list[Citation] = Field(min_length=1)


class MoneyShelfBlock(BaseModel):
    """Capital stack + bioregion-scoped revenue streams for a site."""

    model_config = _FROZEN

    block_type: str = Field(default="money_shelf", frozen=True)
    site_id: str
    bioregion: str                             # revenue streams are fresh for THIS bioregion
    capital_sources: list[CapitalSource] = Field(min_length=1)
    revenue_streams: list[RevenueStream] = Field(min_length=1)
    refresh_note: str = ("Revenue streams are regenerated per bioregion (standing registry, "
                         "quarterly) — mitigation-bank service areas are watershed-scoped.")

    @model_validator(mode="after")
    def _streams_match_bioregion(self) -> "MoneyShelfBlock":
        # every stream must declare a scope (bioregion binding is the point)
        for s in self.revenue_streams:
            if not s.bioregion_scope:
                raise ValueError(f"revenue stream '{s.name}': bioregion_scope required (fresh-per-bioregion rule)")
        return self

    def concessionary_first(self) -> list[CapitalSource]:
        return sorted(self.capital_sources, key=lambda c: (not c.concessionary, c.category))
