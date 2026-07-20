"""Page-shaping — typed payload blocks -> the MAS_PN JSON each __any shell binds.

This is the MAS_PRESENTATION layer DERIVED from FROM_SIR + MAS_DERIVED (not stored
markup), per MAS_Two_Inventories. Structure selects the map/vulnerability units:
single-asset -> zones[], corridor -> segments[]. Numbers pass through the payload
(shaped from the deterministic core); nothing is computed here.
"""
from __future__ import annotations

# Contract keys per page — the shape each __any shell's JS reads (from its data-bind-*
# attributes + MAS_Pn.* reads). Validated in tests/test_render_export.py.
PAGE1_KEYS = {"strings", "blocks", "calc"}
PAGE4_KEYS = {"strings", "blocks", "map", "segment_zones", "projects", "bridges",
              "industries", "industries_revenue_label", "proj_pop", "calc", "proj_pop_text"}

PAGE2_KEYS = {"strings", "blocks", "map", "econ", "calc"}
PAGE3_KEYS = {"strings", "blocks", "segments", "map_features", "insight", "calc"}
PAGE5_KEYS = {"strings", "blocks", "storage_prefix", "opportunities", "hazards", "closure", "CALC"}
PAGE6_KEYS = {"strings", "blocks", "scen", "rows", "local", "calc", "trigger_csv_rows"}
PAGE_DEEPDIVE_KEYS = {"strings", "blocks", "storage_prefix", "LS", "OPP", "STAKE",
                      "STAKE_ORDER", "MONEY", "TROPHY", "CALC", "STORIES"}

_ZONE_COLORS = ["#4A6B8A", "#C8202F", "#f59e0b", "#319795", "#047857", "#B07D1A"]
_FACTORY = "\U0001F3ED"   # 🏭 (mapped to inline SVG by the shell's emoji layer)
_TBF = "[TO_BE_FILLED]"


def _geom_units(payload: dict) -> tuple[list, str, str]:
    """The structure's map/vulnerability units + the id key + unit word.
    single-asset -> zones[]; corridor -> segments[]."""
    meta, blocks = payload["meta"], payload["blocks"]
    geom = blocks.get("geometry", {})
    if meta.get("structure") == "single-asset":
        return geom.get("zones", []), "zone_id", "zones"
    return geom.get("segments", []), "segment_id", "segments"


def _center(payload: dict) -> list:
    geom = payload["blocks"].get("geometry", {})
    if geom.get("lat") is not None:
        return [geom["lat"], geom["lon"]]
    units, _, _ = _geom_units(payload)
    return [units[0].get("lat"), units[0].get("lon")] if units else [0, 0]


def page_1(payload: dict) -> dict:
    """Welcome / decision-gate page (1_welcome__any). Identity + the confirm-asset gate.
    No priced figures on this page — asset_reveal/hero copy stay TO_BE_FILLED until a
    presentation-author or an MAS_DERIVED summary fills them (honest empty, not invented)."""
    meta = payload["meta"]
    name = meta.get("name", "")
    return {
        "strings": {
            "version": f"{name} · {meta.get('as_of') or ''}".strip(" ·"),
            "page_title": f"MAS — {name}",
            "btn_yes": f"Yes, {name}",
            "loading_text": "Preparing the briefing…",
            "loading_sub": f"Compiling {name}",
            "confirm_no_prompt": "Tell me which asset you're evaluating and I'll re-point the briefing.",
        },
        "blocks": {
            "hero_illustration": "",                         # optional hero graphic slot
            "hero_sub": f"Resilience &amp; decision support for <strong>{name}</strong>.",
            "welcome_briefing": f"This briefing covers <strong>{name}</strong> "
                                f"({meta.get('ecological_archetype', '')} · {meta.get('structure', '')}). "
                                f"Confirm the asset to continue.",
            "asset_reveal": _TBF,                            # MAS_DERIVED asset-at-risk summary
        },
        "calc": {},
    }


def page_4(payload: dict) -> dict:
    """Map / committed-baseline page. single-asset -> zones; corridor -> segments.
    Projects/industries are left [] (TO_BE_FILLED) until a committed-baseline / VIP
    block is wired — honest empty, never invented."""
    meta = payload["meta"]
    blocks = payload["blocks"]
    geom = blocks.get("geometry", {})
    structure = meta.get("structure")
    name = meta.get("name", "")

    units = geom.get("zones", []) if structure == "single-asset" else geom.get("segments", [])
    seg_key = "zone_id" if structure == "single-asset" else "segment_id"

    segment_zones = []
    for i, u in enumerate(units):
        color = u.get("color") or _ZONE_COLORS[i % len(_ZONE_COLORS)]
        segment_zones.append({
            "seg": u.get(seg_key),
            "grad": [color, color],
            "emoji": _FACTORY,
            "label": u.get("name", u.get(seg_key)),
            "fly": [u.get("lat"), u.get("lon"), 15],
        })

    if geom.get("lat") is not None:
        center = [geom["lat"], geom["lon"]]
    elif units:
        center = [units[0].get("lat"), units[0].get("lon")]
    else:
        center = [0, 0]

    unit_word = "zones" if structure == "single-asset" else "segments"
    return {
        "strings": {
            "version": f"{name} · {meta.get('as_of') or ''}".strip(" ·"),
            "tab_risk": f"Risk Report: {name}",
            "tab_map": "Committed Baseline & Asset Map",
            "tab_scenario": "Add'l High-ROI Opportunities",
            "section_header": "Committed Baseline — Prior Resilience Work",
            "projects_title": f"Committed Baseline — {name}",
            "industries_title": "Sectors Benefiting from These Mitigations",
            "map_label": name,
            "zoom_btn_label": "⇲ Zoom to full view",
            "zoom_btn_title": f"Zoom to {name}",
            "roi_cluster_label": "Regional cluster",
            "roi_corridor_label": name,
        },
        "blocks": {
            "map_legend": "<div class=\"legend-title\">Committed-baseline status</div>",
            "additionality_banner": "Every opportunity MAS prices is net-new — counted on top of the committed baseline, never re-counting benefits those already deliver.",
            "projects_intro": f"Committed / completed resilience work this asset's {unit_word} build on — prior work, so new-opportunity value is priced net-new.",
            "valero_context": "Baseline items set the additionality floor for opportunity pricing.",
        },
        "map": {"center": center, "zoom": 13, "terminus_bounds": None, "corridor_wide_ids": []},
        "segment_zones": segment_zones,
        "projects": [],                 # committed-baseline projects — TO_BE_FILLED from a baseline block
        "bridges": [],                  # corridor-only NBI overlay
        "industries": [],               # sectors — TO_BE_FILLED from vips/economy
        "industries_revenue_label": "Avoided-loss / EBITDA protected — illustrative",
        "proj_pop": {},
        "calc": {"project": {"title": "Committed-baseline status",
                             "explain": "Baseline items are reported prior work; ROI = n/a (not a new MAS opportunity).",
                             "sources": []}},
        "proj_pop_text": {"assumptions": "Committed baseline — prior work, not priced by MAS.",
                          "calc_prefix": "n/a — baseline item; "},
    }


def _map_segs(payload: dict) -> list:
    """Geometry units -> the map-marker shape pages 2 & 3 plot (lat/lng/label/color)."""
    units, key, _ = _geom_units(payload)
    segs = []
    for i, u in enumerate(units):
        segs.append({
            "lat": u.get("lat"), "lng": u.get("lon"), "n": i + 1,
            "name": u.get("name", u.get(key)),
            "lvl": u.get("exposure") or "—", "hz": "—", "fact": "",
            "c": u.get("color") or _ZONE_COLORS[i % len(_ZONE_COLORS)],
        })
    return segs


def _prefix(payload: dict) -> str:
    return f"mas_{payload['meta'].get('site_id', 'site')}_"


def page_2(payload: dict) -> dict:
    """Landing / context map (2_landing__any). Plots the asset's units + local-economy /
    ecological anchors. Anchor grids + projection charts are MAS_DERIVED — empty until sourced."""
    name = payload["meta"].get("name", "")
    return {
        "strings": {
            "page_title": f"MAS — {name}",
            "closure_popup": "Observed disruption locus.",
            "horizon_pop": "<br>Proposed / non-obligated (§H2) — sensitivity only.",
            "commuter_popup": "Commuter flow — directional context.",
            "welcome_no_bubble": "Tell me the asset you're evaluating and I'll re-point the briefing.",
            "demo_question": f"What are the top resilience opportunities for {name}?",
        },
        "blocks": {},                       # anchor grids / horizon box: MAS_DERIVED, not yet sourced
        "map": {"segs": _map_segs(payload), "bridges": [], "gauges": [], "chokes": []},
        "econ": {"pts": [], "eco": []},     # economic + ecological anchors — TO_BE_FILLED (VIP/receptor blocks)
        "calc": {},
    }


def page_3(payload: dict) -> dict:
    """Risk report (3_risk__any). Plots asset units; the vulnerability cards + hazard
    timeline are MAS_DERIVED (hazard-screen source) — empty until wired."""
    meta = payload["meta"]
    name = meta.get("name", "")
    units, key, _ = _geom_units(payload)
    segments = [{"segment_id": u.get(key), "lat": u.get("lat"), "lon": u.get("lon")} for u in units]
    return {
        "strings": {
            "page_title": f"Risk Report — {name}",
            "corridor_name": name,
            "zoom_title": f"Zoom to full {name} view",
            "workforce_label": "Workforce access (disruption days/yr)",
        },
        "blocks": {},                       # chatbox_detail / triggers_table / insight_cards: MAS_DERIVED
        "segments": segments,               # no .vulnerability yet -> cards render empty (honest)
        "map_features": _map_segs(payload),
        "insight": {},
        "calc": {},
    }


def page_5(payload: dict) -> dict:
    """Scenario builder (5_scenario__any). The opportunity menu is MAS_DERIVED
    (OpportunityMenuBlock); until a priced menu is attached, opportunities is empty."""
    meta = payload["meta"]
    name = meta.get("name", "")
    return {
        "strings": {
            "page_title": f"Scenario Builder — {name}",
            "tab_risk": "Risk Report", "tab_projects": "Existing Projects",
            "storm_btn": "hazard forecasting", "storm_title": "How MAS's forecasting helps",
            "additionality_baseline": "the committed baseline",
            "phasing_note": "Phasing is directional — magnitudes pending pricing.",
            "zoom_label": f"{name}",
        },
        "blocks": {},                       # closure_chain: MAS_DERIVED
        "storage_prefix": _prefix(payload),
        "opportunities": [],                # priced menu (compose) not attached in the thin vertical
        "hazards": {"screening": []},
        "closure": None,
        "CALC": {},
    }


def page_6(payload: dict) -> dict:
    """Combined benefits (6_combined__any). The scenario timeline + decision tables are
    MAS_DERIVED (compose over the opportunity menu) — scaffold only until priced."""
    meta = payload["meta"]
    name = meta.get("name", "")
    version = f"{name} · {meta.get('as_of') or ''}".strip(" ·")
    _flag = lambda bg, tone, tab: {"sumbg": bg, "tone": tone, "tab": tab,
                                   "summary": "Directional severity — magnitudes pending pricing.",
                                   "asset": {}, "local": {}}
    return {
        "strings": {
            "version": version, "page_subtitle": f"Combined resilience benefits — {name}",
            "scenario_banner": "Directional severity — magnitudes pending pricing.",
            "scenario_footnote": "Cells show directional severity only; no dollar magnitudes (pre-pricing).",
            "csv_corridor_header": "ASSET", "atrisk_title": "Existing projects at risk",
            "chatbox_placeholder": f"Ask MAS about {name}…",
        },
        "blocks": {},                       # banners / tables / popups: MAS_DERIVED
        "scen": {"red": _flag("#fdecea", "#C8202F", "#C8202F"),
                 "yellow": _flag("#fff7e6", "#B07D1A", "#B07D1A"),
                 "green": _flag("#eef6f1", "#047857", "#047857")},
        "rows": [], "local": [],            # severity rows: MAS_DERIVED, not sourced -> empty table body
        "calc": {},
        "trigger_csv_rows": [["Trigger", "Threshold", "Action", "~When"]],
    }


def page_deepdive(payload: dict, opp_id: str = "") -> dict:
    """Opportunity deep-dive (5.1_deepdive__any). Per-opportunity money/trophy stacks +
    J-curve. Numbers are MAS_DERIVED via compose (never in-browser) — LS/MONEY/TROPHY
    stay zero/empty here so nothing is fabricated; a priced opportunity fills them."""
    meta = payload["meta"]
    name = meta.get("name", "")
    return {
        "strings": {"title": f"Opportunity Deep-Dive — {name}", "ver": meta.get("as_of") or "",
                    "h1": _TBF, "money_h2": "Money & Trophy Shelf", "overlap_note": "",
                    "practical_lead": name},
        "blocks": {},                       # xs_card / vc_card / tiles_block / loc_card / status_body: MAS_DERIVED
        "storage_prefix": _prefix(payload),
        "LS": {"capex": 0, "restorAcres": 0, "creditPerAc": 0, "creditPrice": 0},   # unsourced -> no fabricated $
        "OPP": {"id": opp_id, "title": _TBF},
        "STAKE": {}, "STAKE_ORDER": [],
        "MONEY": [], "TROPHY": [],
        "CALC": {}, "STORIES": {},
    }
