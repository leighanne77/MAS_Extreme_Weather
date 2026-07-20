"""match_opportunities — deterministic typology filter over the NbS catalog.

Keeps only nature-based solutions whose suitable_locations AND risk_types
intersect the site. A microgrid (gray, not in the NbS catalog) is never returned
— that's the exclusion, done by data, not by the agent.
"""
from __future__ import annotations

import json
from pathlib import Path

_NBS = Path(__file__).resolve().parents[2] / "multi_agent_system" / "data" / "nature_based_solutions.json"

# NbS risk_type -> opportunity lever(s) it enhances (taxonomy ids)
_LMASR_BY_RISK = {
    "flooding": ["revenue_continuity"], "flood": ["revenue_continuity"],
    "sea_level_rise": ["revenue_continuity"], "storm_surge": ["revenue_continuity"],
    "coastal_erosion": ["revenue_continuity"], "erosion": ["revenue_continuity"],
    "extreme_heat": ["opex_reduction"], "drought": ["opex_reduction"],
}


def _norm(xs) -> set[str]:
    return {str(x).lower().replace(" ", "_") for x in (xs or [])}


def match_opportunities(site_locations, site_hazards) -> list[dict]:
    """Return typology-matched NbS opportunities for a site (deterministic)."""
    sols = json.loads(_NBS.read_text())["solutions"]
    locs, haz = _norm(site_locations), _norm(site_hazards)
    out: list[dict] = []
    for s in sols:
        s_locs, s_risks = _norm(s.get("suitable_locations")), _norm(s.get("risk_types"))
        loc_hit, risk_hit = s_locs & locs, s_risks & haz
        if loc_hit and risk_hit:
            levers = {"ecosystem_services", "execution_derisk"}
            for r in risk_hit:
                levers.update(_LMASR_BY_RISK.get(r, []))
            out.append({"id": s["id"], "name": s["name"], "kind": "NbS",
                        "lever_ids": sorted(levers),
                        "matched_locations": sorted(loc_hit),
                        "matched_hazards": sorted(risk_hit)})
    return out
