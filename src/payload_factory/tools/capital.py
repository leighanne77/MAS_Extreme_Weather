"""attach_capital — Money Shelf matcher: which capital funds an opportunity."""
from __future__ import annotations

import json
from pathlib import Path

_FUND = Path(__file__).resolve().parents[2] / "multi_agent_system" / "data" / "funding_sources_NSB.json"


def attach_capital(opportunity_kind: str) -> dict:
    """Return capital sources whose eligible_uses fit the opportunity (concessionary
    flagged). Insurance excluded (eve-no-insurance)."""
    cats = json.loads(_FUND.read_text())["nature_based_solutions_funding"]["funding_sources"]
    sources = []
    for c in cats:
        for s in c["sources"]:
            if "insurance" in s["name"].lower():
                continue
            sources.append({"name": s["name"], "category": c["category"],
                            "eligible_uses": s.get("eligible_uses", []),
                            "url": s.get("learn_more")})
    return {"opportunity_kind": opportunity_kind, "capital_sources": sources,
            "count": len(sources)}
