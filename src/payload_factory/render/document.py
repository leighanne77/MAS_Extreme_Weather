"""Render blocks to MAS-brand document HTML (pure; all I/O at callers).

StrictUndefined = closed-world in the template engine: a missing value
raises; it never renders blank.
"""
from __future__ import annotations

from datetime import date

from jinja2 import Environment, PackageLoader, StrictUndefined

from payload_factory.models.blocks import HazardObsBlock

_env = Environment(
    loader=PackageLoader("payload_factory.render", "templates"),
    autoescape=True,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_hazard_section(block: HazardObsBlock, *, doc_title: str,
                          doc_type: str = "Internal", as_of: date | None = None) -> str:
    """Standalone MAS-brand HTML document for one hazard-observations block."""
    events: list[str] = []
    for o in block.observations:
        if o.event not in events:
            events.append(o.event)
    by_key = {(o.station_id, o.event): o for o in block.observations}
    tpl = _env.get_template("hazard_section.html.j2")
    return tpl.render(block=block, events=events, by_key=by_key,
                      doc_title=doc_title, doc_type=doc_type,
                      as_of=(as_of.isoformat() if as_of else ""))


def _collect_sources(seg, hz, closures, demand, structures=None) -> list[dict]:
    """Unique source rows derived from every citation in the blocks (§17)."""
    cites = list(seg.citations) + list(closures.citations)
    if structures is not None:
        cites.extend(structures.citations)
    for a in demand.anchors:
        cites.extend(a.citations)
    for o in hz.observations:
        for fig in (o.peak_storm_tide, o.peak_residual):
            if fig is not None:
                cites.extend(fig.citations)
    for e in closures.events:
        if e.days_closed is not None:
            cites.extend(e.days_closed.citations)
    seen: dict[str, dict] = {}
    for c in cites:
        if c.source not in seen:
            seen[c.source] = dict(source=c.source, url=(str(c.url) if c.url else None),
                                  preference=c.preference.value, continuity=c.continuity.value,
                                  provenance=c.provenance.value)
    return list(seen.values())


def render_document(*, doc_title: str, standard_name: str, site_id: str, customer: str,
                 version: str, as_of: date, doc_type: str, overview: str,
                 metadata: list[dict], connectivity: list[dict], stakeholders: list[dict], vips,
                 seg, structures, hz, closures, demand, providers, opps_menu, routing: list[dict], coas: list[dict],
                 ilk: list[dict], awards: list[dict], money,
                 amendments: list[dict], triggers: list[dict] | None = None,
                 vuln_matrix: list[dict] | None = None, projects: list[dict] | None = None,
                 horizon: list[dict] | None = None, governance_map: list[dict] | None = None,
                 health_receptors: list[dict] | None = None, eco_receptors: list[dict] | None = None,
                 governance_source: dict | None = None, demand_signals: list[dict] | None = None, source_discovery: list[dict] | None = None, site_media: list[dict] | None = None, hazard_screen: list[dict] | None = None) -> str:
    """Full payload document from typed blocks + framing rows (pure)."""
    hz_events: list[str] = []
    for o in hz.observations:
        if o.event not in hz_events:
            hz_events.append(o.event)
    hz_by_key = {(o.station_id, o.event): o for o in hz.observations}
    tpl = _env.get_template("payload_document.html.j2")
    return tpl.render(doc_title=doc_title, standard_name=standard_name, site_id=site_id,
                      customer=customer, version=version, as_of=as_of.isoformat(),
                      doc_type=doc_type, overview=overview, metadata=metadata,
                      connectivity=connectivity, stakeholders=stakeholders, vips=vips.with_distances(),
                      opps=opps_menu.opportunities, scenarios=[dict(label=s.label, flag=s.flag, selected_ids=s.selected_ids, narrative=s.narrative, status=opps_menu.compose(s.selected_ids)['status']) for s in opps_menu.scenarios], opp_register=opps_menu.register_frame,
                      seg=seg, structures=structures, hz=hz, hz_events=hz_events,
                      hz_by_key=hz_by_key, closures=closures, demand=demand,
                      routing=routing, coas=coas, ilk=ilk, providers=providers.with_distances(), awards=awards,
                      capital=[dict(name=c.name, category=c.category, capital_type=c.capital_type,
                                    concessionary=c.concessionary, discount_note=c.discount_note,
                                    url=str(c.citations[0].url) if c.citations[0].url else None)
                               for c in money.concessionary_first()],
                      revenue=[dict(name=r.name, credit_type=r.credit_type, bioregion_scope=r.bioregion_scope,
                                    market_status=r.market_status, revenue_basis=r.revenue_basis, vocab_note=r.vocab_note,
                                    url=str(r.citations[0].url) if r.citations[0].url else None)
                               for r in money.revenue_streams],
                      money_refresh=money.refresh_note, amendments=amendments, triggers=triggers, vuln_matrix=vuln_matrix, projects=projects, horizon=horizon, governance_map=governance_map,
                      health_receptors=health_receptors, eco_receptors=eco_receptors, governance_source=governance_source, demand_signals=demand_signals, source_discovery=source_discovery,
                      site_media=site_media, hazard_screen=hazard_screen, sources=_collect_sources(seg, hz, closures, demand, structures))
