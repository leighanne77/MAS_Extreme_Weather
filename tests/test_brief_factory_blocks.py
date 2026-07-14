"""brief_factory block models — the house rules, enforced by type system.

Done-means for T2: a figure without a citation CANNOT exist; the SR-37
spike JSON builds a valid block; round-trips are lossless.
"""
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from enums import FigureStatus
from brief_factory.adapters.coops import SR37_STATIONS, block_from_spike
from brief_factory.models.blocks import (
    CalcTrace,
    Citation,
    Figure,
    GaugeEventObservation,
    HazardObsBlock,
)

FIXTURES = Path(__file__).parent / "fixtures"
ACCESSED = date(2026, 7, 13)


def _citation(**over):
    kw = dict(source="NOAA CO-OPS station 9414290", url="https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290",
              accessed=ACCESSED)
    kw.update(over)
    return Citation(**kw)


def _figure(**over):
    kw = dict(label="peak storm tide", value=Decimal("7.68"), unit="ft MLLW",
              status=FigureStatus.VERIFIED, kind="observed", citations=[_citation()])
    kw.update(over)
    return Figure(**kw)


# ── the rules bite ──────────────────────────────────────────────────────────

def test_figure_without_citation_cannot_exist():
    with pytest.raises(ValidationError, match="citations"):
        Figure(label="naked", value=Decimal("1"), unit="ft",
               status=FigureStatus.VERIFIED, citations=[])


def test_computed_figure_requires_calc_trace():
    with pytest.raises(ValidationError, match="calc_trace"):
        _figure(kind="computed")


def test_projected_figure_requires_model_ref():
    with pytest.raises(ValidationError, match="model_ref"):
        _figure(kind="projected")


def test_citation_requires_url_or_reason():
    with pytest.raises(ValidationError, match="url_absent_reason"):
        _citation(url=None)
    ok = _citation(url=None, url_absent_reason="portal download; no stable URL")
    assert ok.url is None


def test_reported_negative_cannot_carry_figures():
    with pytest.raises(ValidationError, match="cannot carry figures"):
        GaugeEventObservation(station_id="9415218", event="AR Jan 2017",
                              status=FigureStatus.REPORTED_NEGATIVE,
                              no_data_reason="record ended 2012",
                              peak_storm_tide=_figure())


def test_reported_negative_requires_reason():
    with pytest.raises(ValidationError, match="no_data_reason"):
        GaugeEventObservation(station_id="9415218", event="AR Jan 2017",
                              status=FigureStatus.REPORTED_NEGATIVE)


def test_frozen_blocks_are_immutable():
    fig = _figure()
    with pytest.raises(ValidationError):
        fig.value = Decimal("9.99")


# ── the SR-37 fixture builds a real block ──────────────────────────────────

@pytest.fixture(scope="module")
def sr37_block() -> HazardObsBlock:
    obs = json.loads((FIXTURES / "sr37_water_spike_obs.json").read_text())
    return block_from_spike(obs, SR37_STATIONS, site_id="sr37-vallejo-ca",
                            hazard="coastal water level / storm surge",
                            accessed=ACCESSED)


def test_sr37_block_shape(sr37_block):
    assert len(sr37_block.stations) == 5
    assert len(sr37_block.observations) == 35  # 5 stations x 7 events
    ok = [o for o in sr37_block.observations if o.status == FigureStatus.VERIFIED]
    gaps = [o for o in sr37_block.observations if o.status == FigureStatus.REPORTED_NEGATIVE]
    assert len(ok) == 18 and len(gaps) == 17


def test_sr37_known_values(sr37_block):
    jan17 = {o.station_id: o for o in sr37_block.observations if o.event == "AR Jan 2017"}
    assert jan17["9415102"].peak_residual.value == Decimal("2.21")   # Martinez amplification
    assert jan17["9414290"].peak_residual.value == Decimal("1.47")   # SF validation gauge
    assert jan17["9415218"].status == FigureStatus.REPORTED_NEGATIVE  # Mare Island dark


def test_sr37_gaps_carry_reasons(sr37_block):
    for o in sr37_block.observations:
        if o.status == FigureStatus.REPORTED_NEGATIVE:
            assert o.no_data_reason


def test_residuals_carry_calc_trace(sr37_block):
    for o in sr37_block.observations:
        if o.peak_residual is not None:
            assert o.peak_residual.calc_trace is not None
            assert o.peak_residual.kind == "computed"


def test_round_trip_lossless(sr37_block):
    dumped = sr37_block.model_dump(mode="json")
    assert HazardObsBlock.model_validate(dumped) == sr37_block


def test_json_schema_generates():
    schema = HazardObsBlock.model_json_schema()
    assert "properties" in schema and "observations" in schema["properties"]
