"""FHWA NBI delimited file -> StructuresBlock (deterministic, from escrowed file).

NBI packs coordinates as DMS: LAT_016 = DDMMSSss, LONG_017 = DDDMMSSss
(seconds x100; longitude west-positive in the file -> negated).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pandas as pd

from enums import DataProvenance, PreferenceClass, SourceContinuity

from payload_factory.models.blocks import Citation
from payload_factory.models.corridor import StructurePoint, StructuresBlock


def _dms(packed: float) -> float:
    v = int(packed)
    return v // 1000000 + ((v // 10000) % 100) / 60 + ((v % 10000) / 100) / 3600


def structures_from_nbi(csv_path: str, *, route: int, county_codes: list[int],
                        site_id: str, accessed: date,
                        segment_map: dict[str, str] | None = None) -> StructuresBlock:
    df = pd.read_csv(csv_path, low_memory=False)
    rows = df[(pd.to_numeric(df["ROUTE_NUMBER_005D"], errors="coerce") == route)
              & (df["COUNTY_CODE_003"].isin(county_codes))]
    seg = segment_map or {}
    structures = []
    for _, r in rows.iterrows():
        sid = str(r["STRUCTURE_NUMBER_008"]).strip()
        lat, lon = r["LAT_016"], r["LONG_017"]
        if pd.isna(lat) or pd.isna(lon) or int(lat) == 0:
            continue
        cond = "/".join(str(r.get(c, "N")).strip() or "N" for c in
                        ("DECK_COND_058", "SUPERSTRUCTURE_COND_059", "SUBSTRUCTURE_COND_060"))
        structures.append(StructurePoint(
            structure_id=sid,
            crosses=str(r["FEATURES_DESC_006A"]).strip().strip("'"),
            year_built=int(r["YEAR_BUILT_027"]),
            condition=cond,
            length_m=Decimal(str(round(float(r["STRUCTURE_LEN_MT_049"]), 1))),
            lat=round(_dms(lat), 5), lon=round(-_dms(lon), 5),
            segment_id=seg.get(sid),
        ))
    citation = Citation(
        source="FHWA National Bridge Inventory 2024 — California delimited file (CA24)",
        publisher="Federal Highway Administration",
        url="https://www.fhwa.dot.gov/bridge/nbi/2024/delimited/CA24.txt",
        accessed=accessed, provenance=DataProvenance.API,
        preference=PreferenceClass.P1_PREFERENCED,       # authority's own record
        continuity=SourceContinuity.TRUSTED_EXCEPTION,
        note="Escrowed copy: data/curated/nbi/CA24.txt (sha256 in escrow manifest, F4)")
    return StructuresBlock(site_id=site_id, structures=structures, citations=[citation])
