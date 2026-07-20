"""resolve_bioregion behavior (2026-07-17).

US site -> archetype + EPA + USACE; international site -> GET-only (no EPA/USACE);
spatially-derived fields carry the [INFERRED — verify] tag; GET biome is required.
"""
import pytest
from pydantic import ValidationError

from payload_factory.tools.bioregion import resolve_bioregion, classification_for_site
from payload_factory.models import BioregionClassification, IucnGet


def test_us_point_resolves_to_coastal_estuarine_with_epa_and_usace():
    bc = resolve_bioregion(38.11, -122.40, "US", state="CA", county="Solano")
    assert bc.ecological_archetype.value == "coastal-estuarine"
    assert bc.iucn_get.biome.startswith("MFT1")           # GET pivot
    assert bc.us_epa is not None and bc.us_epa.l1 == "Mediterranean California"
    assert bc.usace is not None
    assert bc.usace.hgm_class == "Estuarine / Tidal Fringe"   # USACE = regulatory gate only
    # funding is archetype-level (money_path), gated by USACE §404 here
    assert "USACE Beneficial Use Program" in bc.money_path.funding_sources
    assert bc.money_path.regulatory_gate.value == "usace_404_budm"


def test_international_point_is_get_only_but_still_has_funding():
    bc = resolve_bioregion(51.95, 4.14, "NL", get_biome="MFT1", structure="single-asset")
    assert bc.ecological_archetype.value == "coastal-estuarine"  # SAME archetype as the US coastal site
    assert bc.structure.value == "single-asset"
    assert bc.us_epa is None                              # no EPA outside the US
    assert bc.usace is None                               # no USACE regulatory gate outside the US
    assert "[INFERRED — verify]" in (bc.iucn_get.efg or "")
    # the fix: funding still resolves internationally — NOT nested under (absent) USACE
    assert bc.money_path is not None
    assert bc.money_path.regulatory_gate.value == "local_regulator"
    assert bc.money_path.funding_sources == []           # US-federal funding names dropped abroad
    assert bc.money_path.nbs_ids                          # NbS solution ids still apply globally


def test_inferred_tag_on_spatially_derived_fields():
    bc = resolve_bioregion(51.95, 4.14, "NL", get_biome="T5")   # arid via GET
    assert bc.ecological_archetype.value == "arid-desert"
    # ELU factors are per-point in principle; offline they echo defaults, tagged inferred
    tagged = [v for v in vars(bc.un_elu).values() if v]
    assert tagged and all("[INFERRED — verify]" in v for v in tagged)


def test_from_sir_accessor_returns_binding():
    bc = classification_for_site("sr37-vallejo-ca")
    assert bc is not None and bc.ecological_archetype.value == "coastal-estuarine"
    assert classification_for_site("no-such-site") is None


def test_get_biome_is_required_by_the_model():
    with pytest.raises(ValidationError):
        BioregionClassification(ecological_archetype="coastal-estuarine", iucn_get=IucnGet(biome=""))
