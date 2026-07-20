"""Opportunity-Zone check + QOF Money-Shelf benefits (deterministic).

If a site's census tract is a designated Qualified Opportunity Zone, the payload
flags it and the Money Shelf gains the QOF capital benefits. OZ is FEDERAL policy
in transition (2026-27) — the tax specifics carry a hard VERIFY (federal-2026
discipline: vintage-pinned, re-checked yearly).
"""
from __future__ import annotations

import json
from pathlib import Path

_OZ = Path(__file__).resolve().parents[2] / "multi_agent_system" / "data" / "opportunity_zones.json"


def _data() -> dict:
    return json.loads(_OZ.read_text())


def check_opportunity_zone(tract_geoid: str) -> dict:
    """Is this census tract a designated OZ? Reads the local snapshot (fast/offline).
    If the snapshot is partial and the tract isn't listed, the caller should fall
    back to opportunity_zone_api.get_opportunity_zone_by_tract (live)."""
    d = _data()
    tracts = set(d.get("designated_tracts", []))
    md = d.get("metadata", {})
    is_oz = tract_geoid in tracts
    return {
        "tract": tract_geoid,
        "is_opportunity_zone": is_oz,
        "source": md.get("source"),
        "vintage": md.get("designation_vintage"),
        "policy_status": md.get("policy_status"),
        "snapshot_complete": md.get("last_filled") is not None,   # False until build_oz_snapshot ran
        "benefits": qof_benefits() if is_oz else [],
    }


def qof_benefits() -> list[dict]:
    """QOF capital benefits (Money-Shelf capital sources). VERIFY current policy."""
    url = "https://www.irs.gov/credits-deductions/opportunity-zones"
    verify = "[VERIFY current OZ policy — in transition 2026-27 (OBBBA); confirm dates + eligibility]"
    return [
        {"name": "Qualified Opportunity Fund — capital-gains deferral", "category": "OZ",
         "capital_type": "tax-credit", "concessionary": True,
         "discount_note": f"defer tax on reinvested capital gains {verify}", "url": url},
        {"name": "QOF — 10-year gain exclusion", "category": "OZ",
         "capital_type": "tax-credit", "concessionary": True,
         "discount_note": f"no tax on QOF appreciation held 10+ years {verify}", "url": url},
    ]


def oz_payload_contribution(tract_geoid: str) -> dict:
    """What an OZ adds to a payload: a §0 metadata row + Money-Shelf capital sources.
    Returns empty contribution if not an OZ (reported explicitly, not silently)."""
    chk = check_opportunity_zone(tract_geoid)
    if chk["is_opportunity_zone"]:
        row = {"k": "Opportunity Zone", "v": f"YES — tract {tract_geoid} is a designated QOZ; "
               f"QOF capital benefits available. {chk['policy_status']}"}
    else:
        confirm = "" if chk["snapshot_complete"] else " (snapshot partial — confirm via live OZ API)"
        row = {"k": "Opportunity Zone", "v": f"No — tract {tract_geoid} not a designated QOZ{confirm}"}
    return {"metadata_row": row, "capital_sources": chk["benefits"]}
