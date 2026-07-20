"""Opportunity selection -> composed ROI (§14, ADR-0019).

Customer-facing value framing is "Opportunities" (MAS = Exit Value Enhancer).
Each opportunity is SELECTABLE and carries its own cited cost, benefit and BCR.
A scenario is a chosen subset (Red/Yellow/Green); the final ROI COMPOSES from the
selected opportunities + a synergy bonus, emitted as a calc_trace (no naked ROI).
Figures may be TO_BE_FILLED — the SELECTION MECHANISM renders regardless, so the
customer sees the menu and the scenarios even before costs are priced.
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from enums import FigureStatus
from payload_factory.models.blocks import CalcTrace, Citation, Figure

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class SelectableOpportunity(BaseModel):
    """One pickable opportunity — its own ROI contribution, cited."""

    model_config = _FROZEN

    id: str
    name: str
    kind: str = Field(pattern="^(Gray|NbS|Hybrid)$")
    lever_ids: list[str] = Field(min_length=1)     # from opportunities.yaml (opex_reduction, ...)
    status: FigureStatus                            # opportunity-level status
    cost: Figure | None = None                      # capital cost (TO_BE_FILLED allowed)
    annual_benefit: Figure | None = None            # avoided loss / revenue (cited)
    bcr: Figure | None = None                       # computed => calc_trace (enforced by Figure)
    synergy_with: list[str] = Field(default_factory=list)
    # shared table (doc 8): outcome per beneficiary lens — keys validated against
    # BeneficiaryClass; optional until builders/agents populate (additive 2026-07-15)
    outcomes: dict[str, str] = Field(default_factory=dict)

    @field_validator("outcomes")
    @classmethod
    def _outcome_keys_are_beneficiary_classes(cls, v: dict) -> dict:
        from enums import BeneficiaryClass
        for k in v:
            BeneficiaryClass(k)          # raises on unknown lens
        return v

    selected: bool = False


class OpportunityScenario(BaseModel):
    """A named selection (Red/Yellow/Green) -> composed ROI."""

    model_config = _FROZEN

    label: str                                      # e.g. "Green Flag - full resilience stack"
    flag: str = Field(pattern="^(red|yellow|green)$")
    internal_id: str | None = None                 # immutable taxonomy id (D/G/A — Mobile canonical pattern); display flag may rename, this never does
    selected_ids: list[str]
    composed_cost: Figure | None = None
    composed_benefit: Figure | None = None
    blended_bcr: Figure | None = None               # calc_trace lists the selected ids + synergy
    synergy_bonus: Figure | None = None
    narrative: str | None = None


class OpportunityMenuBlock(BaseModel):
    """The selectable opportunity menu + scenarios for a site (§14)."""

    model_config = _FROZEN

    block_type: str = Field(default="opportunity_menu", frozen=True)
    site_id: str
    register_frame: str                             # private_equity | government (figures invariant across both)
    opportunities: list[SelectableOpportunity] = Field(min_length=1)
    scenarios: list[OpportunityScenario] = Field(min_length=1)

    def compose(self, selected_ids: list[str]) -> dict:
        """Deterministic ROI composition for a selection (when figures exist).
        Returns totals + a calc_trace; marks pending when any selected figure is absent.
        """
        chosen = [o for o in self.opportunities if o.id in selected_ids]
        if not chosen:                                  # do-nothing baseline (Red flag)
            return {"selected": [], "priced": [], "pending": [], "total_cost": None,
                    "total_annual_benefit": None, "trace": None, "status": "do-nothing"}
        priced = [o for o in chosen if o.cost and o.annual_benefit]
        pending = [o.id for o in chosen if not (o.cost and o.annual_benefit)]
        total_cost = sum((o.cost.value for o in priced), Decimal(0))
        total_benefit = sum((o.annual_benefit.value for o in priced), Decimal(0))
        return {
            "selected": [o.id for o in chosen],
            "priced": [o.id for o in priced],
            "pending": pending,
            "total_cost": total_cost if priced else None,
            "total_annual_benefit": total_benefit if priced else None,
            "trace": CalcTrace(
                formula="blended BCR = sum(selected annual benefits) / annualized sum(selected costs) + synergy bonus",
                inputs={o.id: (str(o.bcr.value) if o.bcr else "TO_BE_FILLED") for o in chosen},
                method_note="No naked ROI: composition lists every selected opportunity and its cited contribution."),
            "status": "priced" if not pending else "partial-pending",
        }
