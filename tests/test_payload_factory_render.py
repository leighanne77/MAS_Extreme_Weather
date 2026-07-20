"""Renderer tests — branded document from the SR-37 block, rules visible."""
import json
from datetime import date
from pathlib import Path

import pytest

from payload_factory.adapters.coops import SR37_STATIONS, block_from_spike
from payload_factory.render import render_hazard_section

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def html() -> str:
    obs = json.loads((FIXTURES / "sr37_water_spike_obs.json").read_text())
    block = block_from_spike(obs, SR37_STATIONS, site_id="sr37-vallejo-ca",
                             hazard="coastal water level / storm surge",
                             accessed=date(2026, 7, 13))
    return render_hazard_section(block, doc_title="SR-37 Corridor — Observed Water Levels",
                                 doc_type="Internal", as_of=date(2026, 7, 13))


def test_known_figures_rendered(html):
    assert "2.21" in html          # Martinez residual, AR Jan 2017
    assert "8.51" in html          # SF storm tide, Feb 1998


def test_gaps_render_as_findings_not_blanks(html):
    assert html.count('class="pill nodata"') == 17
    assert "2012-10-28" in html    # Mare Island record end shown (the gap explained)


def test_every_verified_figure_has_citation_url(html):
    # 18 verified observations -> 18 [src] popovers with station URLs
    assert html.count("[src]") == 18
    assert html.count("tidesandcurrents.noaa.gov") >= 18


def test_brand_and_trust_chrome(html):
    assert "MAS" in html
    assert "#C8202F" in html and "#1A2332" in html and "#E8A82A" in html
    assert "no LLM in the numbers trust path" in html
    assert "p1-preferenced" in html
    assert "trusted-exception" in html


def test_self_contained_no_external_requests(html):
    for marker in ("cdn.", "googleapis", "fontawesome", "http://"):
        assert marker not in html.lower().replace("https://tidesandcurrents", "")
