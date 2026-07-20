"""Export factory — stamp a payload into the archetype-neutral HTML shells.

`render_site(payload)` shapes each page's JSON (render/pages.py) and injects it into
that page's `__MAS_PAGEN__` token in the `__any` shell, producing a self-contained
HTML export view. The shells are package data under `render/templates/mas_pages/`
(the same location convention as the existing `render/templates/*.j2`). `structure`
(single-asset | corridor) already drove the shaping; numbers arrive pre-shaped —
the browser never computes (payload.py contract).

Drop the polished `*__any.html` shells into `render/templates/mas_pages/` to render
them; the page-shaping + injection here are the shell-agnostic mechanism.
"""
from __future__ import annotations

import json
from pathlib import Path

from payload_factory.render import pages as _pages

_MAS_PAGES = Path(__file__).resolve().parent / "templates" / "mas_pages"

# The full shell set: page name -> (shell filename, injection token). See
# render/templates/mas_pages/README.md. Shapers are added to _PAGES as they land.
_PAGE_TOKENS: dict[str, tuple[str, str]] = {
    "page_1": ("1_welcome__any.html", "__MAS_PAGE1__"),
    "page_2": ("2_landing__any.html", "__MAS_PAGE2__"),
    "page_3": ("3_risk__any.html", "__MAS_PAGE3__"),
    "page_4": ("4_map__any.html", "__MAS_PAGE4__"),
    "page_5": ("5_scenario__any.html", "__MAS_PAGE5__"),
    "page_deepdive": ("5.1_deepdive__any.html", "__MAS_PAYLOAD__"),
    "page_6": ("6_combined__any.html", "__MAS_PAGE6__"),
}

# page name -> (shell filename, injection token, shaper). All 7 shapers implemented;
# they render crash-safe from a stamped payload (analytic content honest-empty until sourced).
_PAGES: dict[str, tuple[str, str, object]] = {
    name: (_PAGE_TOKENS[name][0], _PAGE_TOKENS[name][1], shaper)
    for name, shaper in (
        ("page_1", _pages.page_1), ("page_2", _pages.page_2), ("page_3", _pages.page_3),
        ("page_4", _pages.page_4), ("page_5", _pages.page_5), ("page_6", _pages.page_6),
        ("page_deepdive", _pages.page_deepdive),
    )
}

# JS line/paragraph separators are valid JSON but break a JS string literal.
_LS = chr(0x2028)
_PS = chr(0x2029)


def _inject(html: str, token: str, data: dict) -> str:
    """Replace `token` with `data` as JSON, safely embedded inside a
    <script type="application/json"> block: guard `</script>` breakout and the
    JS line-separator hazards (U+2028 / U+2029)."""
    if token not in html:
        raise ValueError(f"injection token {token!r} not found in template")
    s = json.dumps(data, ensure_ascii=False)
    s = s.replace("</", "<\\/").replace(_LS, "\\u2028").replace(_PS, "\\u2029")
    return html.replace(token, s)


def render_page(page_name: str, payload: dict, *, templates_dir: str | Path | None = None) -> str:
    """Shape + inject one page -> self-contained HTML string."""
    fname, token, shaper = _PAGES[page_name]
    tdir = Path(templates_dir) if templates_dir else _MAS_PAGES
    html = (tdir / fname).read_text()
    return _inject(html, token, shaper(payload))


def render_site(payload: dict, *, templates_dir: str | Path | None = None) -> dict[str, str]:
    """Every wired page for a payload -> {filename: html}. Thin vertical = page_4;
    add entries to _PAGES as pages/shells land."""
    out: dict[str, str] = {}
    for name, (fname, _token, _shaper) in _PAGES.items():
        out[fname] = render_page(name, payload, templates_dir=templates_dir)
    return out
