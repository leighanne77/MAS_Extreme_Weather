"""Payload-factory backbone: the three-input stamp (SIR × axes.ecological × axes.structure).

Proves the coastal SINGLE-ASSET path (instance #1) end-to-end, plus the corridor
path via the registered sr37 site. Numbers stay server-side (payload contract).
"""
from datetime import date
from pathlib import Path

import pytest

from enums import CoordConfidence, EcologicalArchetype, SiteStructure
from payload_factory import axes
from payload_factory.models import AssetBlock, AssetZone, BioregionClassification, IucnGet, cite
from payload_factory.sir import SiteInventoryRecord, sir_for
from payload_factory.stamp import stamp_payload


def test_axes_resolve_from_single_source():
    eco = axes.ecological("coastal-estuarine")
    assert eco.hazard_signature and eco.money_path["regulatory_gate"] == "usace_404_budm"
    assert axes.ecological(EcologicalArchetype.ARID_DESERT).money_path["regulatory_gate"] == "state_mar"
    assert axes.structure("single-asset").geometry_block == "AssetBlock"
    assert axes.structure(SiteStructure.CORRIDOR).geometry_block == "SegmentationBlock"
    assert axes.geometry_block_class("single-asset") is AssetBlock


def _coastal_single_asset_sir() -> SiteInventoryRecord:
    """A minimal coastal single-asset SIR (Mobile Naval Yard shape) — instance #1."""
    asset = AssetBlock(
        site_id="mobile-naval-yard", asset_name="Mobile Naval Yard",
        typology=["shipyard", "coastal point-asset"], waterbody="Mobile Bay",
        lat=30.678, lon=-88.027, coord_conf=CoordConfidence.MED,
        zones=[
            AssetZone(zone_id="z1-waterfront", name="Waterfront frontage / berths",
                      lat=30.678, lon=-88.029, coord_conf=CoordConfidence.LOW,
                      exposure="surge + erosion on the water frontage", color="#4A6B8A"),
            AssetZone(zone_id="z2-drydock", name="Drydock & fabrication halls",
                      lat=30.677, lon=-88.026, coord_conf=CoordConfidence.LOW, color="#C8202F"),
        ],
        citations=[cite("USACE Mobile District", "https://www.sam.usace.army.mil/", date(2026, 7, 18))],
    )
    cls = BioregionClassification(
        ecological_archetype="coastal-estuarine", structure="single-asset",
        iucn_get=IucnGet(realm="Marine-Freshwater-Terrestrial (MFT)", biome="MFT1 — Brackish tidal systems"),
    )
    return SiteInventoryRecord(site_id="mobile-naval-yard", name="Mobile Naval Yard",
                               classification=cls, geometry=asset, blocks={"asset": asset},
                               as_of=date(2026, 7, 18))


def test_stamp_coastal_single_asset():
    p = stamp_payload(_coastal_single_asset_sir())
    assert p["meta"]["ecological_archetype"] == "coastal-estuarine"
    assert p["meta"]["structure"] == "single-asset"
    assert p["meta"]["value_model"] == "ebitda_at_risk"          # single-asset investor lens (from axes.structure)
    # THING: the geometry is the AssetBlock (zones), not a corridor
    assert p["blocks"]["geometry"]["block_type"] == "asset"
    assert len(p["blocks"]["geometry"]["zones"]) == 2
    # PLACE: the coastal ecological profile came from axes.ecological
    ep = p["blocks"]["ecological_profile"]
    assert ep["archetype"] == "coastal-estuarine"
    assert ep["money_path"]["regulatory_gate"] == "usace_404_budm"
    assert "living_shoreline" in ep["money_path"]["nbs_ids"]


@pytest.mark.skipif(not (Path(__file__).resolve().parents[1] / "sites" / "sr37-vallejo-ca").exists(),
                    reason="site data lives in the private repo")
def test_stamp_corridor_via_registered_site():
    p = stamp_payload(sir_for("sr37-vallejo-ca"))
    assert p["meta"]["structure"] == "corridor"
    assert p["meta"]["value_model"] == "closure_days_bcr"
    assert p["blocks"]["geometry"]["block_type"] == "corridor_segmentation"


def test_numbers_are_never_computed_in_browser():
    p = stamp_payload(_coastal_single_asset_sir())
    assert "server-side" in p["contract"]["numbers_computed"]
    # the recompute path is declared as data (deterministic core), not baked into UI
    assert p["interactions"]["compute_via"] == "api"
