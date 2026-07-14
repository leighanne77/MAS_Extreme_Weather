"""Render blocks to branded document HTML (pure; all I/O at callers).

StrictUndefined = closed-world in the template engine: a missing value
raises; it never renders blank.
"""
from __future__ import annotations

from datetime import date

from jinja2 import Environment, PackageLoader, StrictUndefined

from brief_factory.models.blocks import HazardObsBlock

_env = Environment(
    loader=PackageLoader("brief_factory.render", "templates"),
    autoescape=True,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_hazard_section(block: HazardObsBlock, *, doc_title: str,
                          doc_type: str = "Internal", as_of: date | None = None) -> str:
    """Standalone branded HTML document for one hazard-observations block."""
    events: list[str] = []
    for o in block.observations:
        if o.event not in events:
            events.append(o.event)
    by_key = {(o.station_id, o.event): o for o in block.observations}
    tpl = _env.get_template("hazard_section.html.j2")
    return tpl.render(block=block, events=events, by_key=by_key,
                      doc_title=doc_title, doc_type=doc_type,
                      as_of=(as_of.isoformat() if as_of else ""))
