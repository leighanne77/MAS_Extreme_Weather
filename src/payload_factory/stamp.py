"""stamp_payload — one payload stamped from THREE inputs.

    SIR (facts)  ×  axes.ecological[archetype] (the PLACE)  ×  axes.structure[structure] (the THING)
        -> tool_payload()  (the data contract the tool/export view consumes)

This replaces the conflated `SiteSpec.standard` selector (`coastal_corridor`) with the
clean (ecological × structure) decomposition. Numbers stay server-side: the manifest
declares the deterministic recompute path (OpportunityMenuBlock.compose), the browser
never computes (payload.py contract).
"""
from __future__ import annotations

from payload_factory import axes
from payload_factory.payload import InteractionManifest, InteractiveSurface, tool_payload
from payload_factory.sir import SiteInventoryRecord


def _manifest(sir: SiteInventoryRecord) -> InteractionManifest:
    """Interactive surfaces derived from the SIR's blocks (register toggle is always present)."""
    surfaces: list[InteractiveSurface] = []
    has_menu = any(getattr(b, "block_type", None) == "opportunity_menu" for b in sir.blocks.values())
    if has_menu:
        surfaces.append(InteractiveSurface(surface_id="opportunity_select", kind="select",
                                           block_ref="opportunity_menu",
                                           recompute="OpportunityMenuBlock.compose"))
        surfaces.append(InteractiveSurface(surface_id="scenario", kind="scenario",
                                           block_ref="opportunity_menu",
                                           options=["red", "yellow", "green"],
                                           recompute="OpportunityMenuBlock.compose"))
    surfaces.append(InteractiveSurface(surface_id="register", kind="toggle",
                                       block_ref="opportunities.yaml",
                                       options=["private_equity", "government"]))
    return InteractionManifest(surfaces=surfaces)


def stamp_payload(sir: SiteInventoryRecord) -> dict:
    """Stamp the payload for a site from its SIR + the two axes it selects."""
    eco = axes.ecological(sir.ecological_archetype)                 # PLACE
    struct = axes.structure(sir.structure)                   # THING

    meta = {
        "site_id": sir.site_id,
        "name": sir.name,
        "as_of": sir.as_of.isoformat() if sir.as_of else None,
        "ecological_archetype": sir.ecological_archetype.value,
        "structure": sir.structure.value,
        "value_model": struct.value_model,
        "html_map": struct.html_map,
        "register_default": "government",
    }

    # blocks = SIR facts (FROM_SIR) + the ecological PLACE profile + the structure-typed geometry.
    blocks: dict = {role: b.model_dump(mode="json") for role, b in sir.blocks.items()}
    blocks["bioregion_classification"] = sir.classification.model_dump(mode="json")
    blocks["ecological_profile"] = eco.model_dump(mode="json")      # hazards / NbS-money menu / crosswalk
    blocks["geometry"] = sir.geometry.model_dump(mode="json")       # zones[] (single-asset) | segments[] (corridor)

    return tool_payload(meta=meta, blocks=blocks, manifest=_manifest(sir))
