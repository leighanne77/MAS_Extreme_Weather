"""Export factory — page-shaping (render/pages.py) + safe injection (render/export.py).

Proves the coastal single-asset render path: AssetBlock zones -> MAS_P4.segment_zones,
injected safely into a shell, self-contained (no external URLs). Uses a compact fixture
shell with the same __MAS_PAGE4__ token/contract as the polished 4_map__any.html.
"""
import json
import re
from pathlib import Path

from payload_factory.render import export, pages
from payload_factory.render.export import _inject
from payload_factory.stamp import stamp_payload

FIXTURES = Path(__file__).resolve().parent / "fixtures"

# reuse the coastal single-asset SIR builder from the stamp test
from test_payload_axes_stamp import _coastal_single_asset_sir  # noqa: E402


def _payload():
    return stamp_payload(_coastal_single_asset_sir())


def test_page1_shape_matches_contract():
    p1 = pages.page_1(_payload())
    assert set(p1) == pages.PAGE1_KEYS
    assert p1["strings"]["page_title"].endswith("Mobile Naval Yard")
    assert "Mobile Naval Yard" in p1["blocks"]["welcome_briefing"]
    assert p1["blocks"]["asset_reveal"] == "[TO_BE_FILLED]"   # honest empty — not invented


def test_all_seven_shells_are_registered_with_tokens():
    from payload_factory.render.export import _PAGE_TOKENS, _PAGES
    assert len(_PAGE_TOKENS) == 7
    assert _PAGE_TOKENS["page_deepdive"] == ("5.1_deepdive__any.html", "__MAS_PAYLOAD__")
    assert _PAGE_TOKENS["page_4"][1] == "__MAS_PAGE4__"
    assert len(_PAGES) == 7                                 # all shapers implemented


def test_all_shapers_produce_their_contracts():
    p = _payload()
    assert set(pages.page_1(p)) == pages.PAGE1_KEYS
    assert set(pages.page_2(p)) == pages.PAGE2_KEYS
    assert set(pages.page_3(p)) == pages.PAGE3_KEYS
    assert set(pages.page_4(p)) == pages.PAGE4_KEYS
    assert set(pages.page_5(p)) == pages.PAGE5_KEYS
    assert set(pages.page_6(p)) == pages.PAGE6_KEYS
    assert set(pages.page_deepdive(p)) == pages.PAGE_DEEPDIVE_KEYS


def test_shapers_are_crash_safe_for_shell_js():
    """Every key the shell JS dereferences at load (.forEach / [k][i]) must exist."""
    p = _payload()
    p2 = pages.page_2(p)
    assert all(k in p2["map"] for k in ("segs", "bridges", "gauges", "chokes"))
    assert all(k in p2["econ"] for k in ("pts", "eco"))
    assert len(p2["map"]["segs"]) == 2                      # the 2 single-asset zones, plotted
    scen = pages.page_6(p)["scen"]                          # render('red') runs on load
    assert set(scen) == {"red", "yellow", "green"}
    assert all("asset" in scen[s] and "local" in scen[s] for s in scen)
    assert pages.page_deepdive(p)["LS"]["capex"] == 0       # compute() numerics present, unsourced=0 (no fabrication)


def test_page4_shape_matches_contract_and_single_asset_zones():
    p4 = pages.page_4(_payload())
    assert set(p4) == pages.PAGE4_KEYS
    labels = [z["label"] for z in p4["segment_zones"]]
    assert "Waterfront frontage / berths" in labels and len(p4["segment_zones"]) == 2
    assert p4["strings"]["map_label"] == "Mobile Naval Yard"
    assert p4["projects"] == [] and p4["industries"] == []   # honest empties — nothing invented


def test_inject_is_script_breakout_safe():
    """A stray </script> or JS line-separator in the data must NOT break the shell."""
    ls, ps = chr(0x2028), chr(0x2029)
    html = '<script id="x" type="application/json">__TOK__</script>'
    out = _inject(html, "__TOK__", {"evil": "</script><script>alert(1)</script>",
                                    "sep": "a" + ls + "b" + ps + "c"})
    assert "</script><script>alert" not in out            # no raw breakout
    assert "<\\/script>" in out                            # escaped instead
    assert ls not in out and ps not in out                 # separators escaped
    payload_str = out.split(">", 1)[1].rsplit("<", 1)[0].replace("<\\/", "</")
    assert json.loads(payload_str)["evil"].startswith("</script>")


def test_render_page_is_self_contained():
    html = export.render_page("page_4", _payload(), templates_dir=FIXTURES)
    assert "Mobile Naval Yard" in html                     # bound + injected
    assert "__MAS_PAGE4__" not in html                     # token consumed
    externals = re.findall(r'(?:src|href)\s*=\s*["\'](?:https?:)?//', html)
    assert not externals, f"external resource refs found: {externals}"
