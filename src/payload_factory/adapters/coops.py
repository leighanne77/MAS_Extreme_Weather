"""NOAA CO-OPS spike-JSON -> HazardObsBlock adapter (deterministic, no fetch).

Consumes the obs JSON written by the spike scripts (mobile_surge_spike.py /
sr37_water_spike.py). Gaps arrive as REPORTED_NEGATIVE with the API's own
status text as the reason — a gap is a finding, never a zero.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from enums import DataProvenance, FigureStatus, Grade, PreferenceClass, SourceContinuity

from payload_factory.models.blocks import (
    CalcTrace,
    Citation,
    Figure,
    GaugeEventObservation,
    GaugeStation,
    HazardObsBlock,
)

_RESIDUAL_TRACE = CalcTrace(
    formula="peak(observed water level − predicted tide) over event window",
    inputs={
        "observed": "NOAA CO-OPS product=water_level (6-min; hourly fallback)",
        "predicted": "NOAA CO-OPS product=predictions",
    },
    method_note="Datum cancels in the subtraction (MLLW used consistently).",
)

# SR-37 corridor station registry (metadata from CO-OPS MDAPI, 2026-07-13)
SR37_STATIONS: list[GaugeStation] = [
    GaugeStation(station_id="9414290", name="San Francisco (Golden Gate)",
                 exposure_role="validation", lat=37.806, lon=-122.466,
                 record_start=date(1854, 6, 30)),
    GaugeStation(station_id="9414863", name="Richmond",
                 exposure_role="bay", lat=37.928, lon=-122.400),
    GaugeStation(station_id="9415102", name="Martinez-Amorco Pier (Carquinez)",
                 exposure_role="asset-proximate", lat=38.035, lon=-122.125),
    GaugeStation(station_id="9415218", name="Mare Island",
                 exposure_role="asset-proximate", lat=38.070, lon=-122.250,
                 record_start=date(1976, 9, 29), record_end=date(2012, 10, 28)),
    GaugeStation(station_id="9415252", name="Petaluma River Entrance",
                 exposure_role="asset-proximate", lat=38.115, lon=-122.506,
                 record_start=date(1977, 5, 10), record_end=date(2014, 7, 10)),
]


def _citation(station_id: str, accessed: date) -> Citation:
    return Citation(
        source=f"NOAA CO-OPS station {station_id}, verified water levels (datum MLLW)",
        publisher="NOAA Center for Operational Oceanographic Products and Services",
        url=f"https://tidesandcurrents.noaa.gov/stationhome.html?id={station_id}",
        accessed=accessed,
        provenance=DataProvenance.API,
        continuity=SourceContinuity.TRUSTED_EXCEPTION,  # observational network
        preference=PreferenceClass.P1_PREFERENCED,      # authority + observed + long record
    )


def _figure(label: str, value: float, unit: str, kind: str,
            station_id: str, accessed: date) -> Figure:
    return Figure(
        label=label,
        value=Decimal(str(value)),
        unit=unit,
        status=FigureStatus.VERIFIED,
        kind=kind,
        citations=[_citation(station_id, accessed)],
        calc_trace=_RESIDUAL_TRACE if kind == "computed" else None,
        grade=Grade.HIGH,
    )


def block_from_spike(obs: dict, stations: list[GaugeStation], *, site_id: str,
                     hazard: str, accessed: date,
                     method_caveat: str | None = None) -> HazardObsBlock:
    """Build a HazardObsBlock from a spike obs JSON dict."""
    observations: list[GaugeEventObservation] = []
    for event, per_station in obs["events"].items():
        for station_id, result in per_station.items():
            if result.get("status") == "ok":
                observations.append(GaugeEventObservation(
                    station_id=station_id, event=event, status=FigureStatus.VERIFIED,
                    peak_storm_tide=_figure(
                        f"peak storm tide — {event}",
                        result["peak_storm_tide_ft_MLLW"]["value"],
                        "ft MLLW", "observed", station_id, accessed),
                    peak_residual=_figure(
                        f"peak non-tidal residual — {event}",
                        result["peak_nontidal_residual_ft"]["value"],
                        "ft", "computed", station_id, accessed),
                ))
            else:
                observations.append(GaugeEventObservation(
                    station_id=station_id, event=event,
                    status=FigureStatus.REPORTED_NEGATIVE,
                    no_data_reason=result.get("status", "no data"),
                ))
    return HazardObsBlock(
        hazard=hazard, site_id=site_id, stations=stations,
        observations=observations,
        method_caveat=method_caveat or obs.get("note"),
    )
