"""attach_recognition — Trophy Shelf matcher: awards an opportunity unlocks."""
from __future__ import annotations

import json
from pathlib import Path

_AWARDS = Path(__file__).resolve().parents[3] / "standards" / "reference" / "awards_registry.json"


def attach_recognition(opportunity_kind: str) -> list[dict]:
    """Return class-eligible awards for the opportunity kind (rule-based)."""
    awards = json.loads(_AWARDS.read_text())["awards"]
    return [{"program": a["program"], "facet": a["facet"], "class": a["class"], "url": a["url"]}
            for a in awards if opportunity_kind in a["eligible_kinds"]]
