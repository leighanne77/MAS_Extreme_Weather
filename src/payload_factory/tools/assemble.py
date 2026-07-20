"""assemble_opportunity_menu — the bridge: tools -> validated OpportunityMenuBlock.

This is what recommendation_agent orchestrates (it calls the tools + ranks/narrates;
the tools do the matching). The block is pydantic-validated on construction, so an
invalid menu cannot be produced. Figures are TO_BE_FILLED (cost data not pulled yet)
— the SELECTION MECHANISM assembles regardless, from data not the LLM.
"""
from __future__ import annotations

from enums import FigureStatus
from payload_factory.models import (
    OpportunityMenuBlock, OpportunityScenario, SelectableOpportunity,
)
from payload_factory.tools.match import match_opportunities


def assemble_opportunity_menu(*, site_id: str, locations, hazards,
                              register_frame: str = "government") -> OpportunityMenuBlock:
    """Deterministic menu for a site, matched from the NbS catalog by typology."""
    matched = match_opportunities(locations, hazards)
    if not matched:
        raise ValueError(f"{site_id}: no typology-matched opportunities (check locations/hazards)")
    opps = [SelectableOpportunity(id=m["id"], name=m["name"], kind=m["kind"],
                                  lever_ids=m["lever_ids"], status=FigureStatus.TO_BE_FILLED)
            for m in matched]
    ids = [o.id for o in opps]
    scenarios = [
        OpportunityScenario(label="Red Flag — do nothing", flag="red", selected_ids=[],
                            narrative="No opportunity taken; exposure compounds on today's steward."),
        OpportunityScenario(label="Yellow Flag — lead NbS only", flag="yellow", selected_ids=ids[:1],
                            narrative="A single lead nature-based move; partial protection."),
        OpportunityScenario(label="Green Flag — full matched stack", flag="green", selected_ids=ids,
                            narrative="All typology-matched opportunities with synergy bonus."),
    ]
    return OpportunityMenuBlock(site_id=site_id, register_frame=register_frame,
                               opportunities=opps, scenarios=scenarios)


def gate_opportunity_menu(block: OpportunityMenuBlock) -> list[str]:
    """The validation_agent lint gate: return violations ([] = passes).
    Construction already enforces types; this adds the taxonomy + kind checks.
    """
    import yaml
    from pathlib import Path
    tax = yaml.safe_load(
        (Path(__file__).resolve().parents[3] / "standards" / "reference" / "opportunities.yaml").read_text())
    known = {o["id"] for r in tax["registers"].values() for o in r["opportunities"]}
    problems = []
    for o in block.opportunities:
        bad = set(o.lever_ids) - known
        if bad:
            problems.append(f"{o.id}: levers not in taxonomy {sorted(bad)}")
        if o.kind not in ("Gray", "NbS", "Hybrid"):
            problems.append(f"{o.id}: invalid kind {o.kind}")
    return problems
