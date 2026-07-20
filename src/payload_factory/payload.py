"""Brief payload = the data contract that POPULATES the MAS tool (ADR-0020).

The Brief is NOT a human document — the HTML renderer is one export view. The
primary artifact is this payload: the compiled blocks (facts + the option space)
+ an interaction manifest that tells the tool what is selectable/toggleable, and
+ field-level provenance carried on every Figure. The tool is a pure renderer over
this payload; NUMBERS ARE NMASR COMPUTED IN THE BROWSER — the deterministic core
(e.g. OpportunityMenuBlock.compose) recomputes via the API, preserving the
'no LLM / no naked ROI' trust path in an interactive setting.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class InteractiveSurface(BaseModel):
    """One thing the tool lets the user manipulate."""

    model_config = _FROZEN

    surface_id: str
    kind: str = Field(pattern="^(select|scenario|toggle|slider)$")
    block_ref: str                              # which block the surface drives
    options: list[str] = Field(default_factory=list)     # select/toggle values
    range: list[str] = Field(default_factory=list)       # slider [min, max, ...]
    recompute: str | None = None                # deterministic fn the API runs on change
    status: str = "live"                        # live | TO_COME


class InteractionManifest(BaseModel):
    """What the tool makes interactive — declared as data, not baked into UI code."""

    model_config = _FROZEN

    surfaces: list[InteractiveSurface] = Field(min_length=1)
    compute_via: str = "api"                    # numbers recomputed server-side (deterministic), never in-browser
    provenance: str = "field-level — every Figure carries citations in the payload"


def tool_payload(*, meta: dict, blocks: dict, manifest: InteractionManifest) -> dict:
    """The single JSON the API serves and the tool consumes (= brief data contract)."""
    return {
        "meta": meta,                           # brief_id, site, standard, version, register_default
        "blocks": blocks,                       # every typed block, model_dump'd (facts + option space)
        "interactions": manifest.model_dump(),  # selectable opportunities, scenarios, register toggle, sliders
        "contract": {
            "numbers_computed": "server-side (deterministic core), never in browser",
            "no_naked_roi": "composed ROI carries a calc_trace listing every selected opportunity",
            "audience_invariance": "register toggle reframes; figures are identical across registers",
            "views": ["interactive tool (primary)", "HTML document / PDF snapshot (export)"],
        },
    }


def sr37_manifest() -> InteractionManifest:
    """The interactive surfaces for the SR-37 Brief."""
    return InteractionManifest(surfaces=[
        InteractiveSurface(surface_id="opportunity_select", kind="select",
                           block_ref="opportunity_menu",
                           recompute="OpportunityMenuBlock.compose"),
        InteractiveSurface(surface_id="scenario", kind="scenario", block_ref="opportunity_menu",
                           options=["red", "yellow", "green"], recompute="OpportunityMenuBlock.compose"),
        InteractiveSurface(surface_id="register", kind="toggle", block_ref="opportunities.yaml",
                           options=["private_equity", "government"]),
        InteractiveSurface(surface_id="slr_scenario", kind="slider", block_ref="model_registry_routing",
                           range=["low", "intermediate", "high"], status="TO_COME"),
        InteractiveSurface(surface_id="year", kind="slider", block_ref="adaptive_pathways",
                           range=["2026", "2050", "2100"], status="TO_COME"),
    ])
