"""GeoJSON emission — one FeatureCollection per Brief (pure).

Keeps geospatial representation honest: every feature carries its class
(gauge / structure / segment-centroid) and coordinate confidence. CRS is
EPSG:4326 (GeoJSON default); corridor line geometry is a named TO_BE_FILLED
until the OSM polyline pull (a centroid chain is NOT a corridor).
"""
from __future__ import annotations


def corridor_geojson(seg, structures, stations) -> dict:
    feats = []
    for st in stations:
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [st.lon, st.lat]},
                      "properties": {"class": "gauge", "id": st.station_id, "name": st.name,
                                     "role": st.exposure_role, "coord_conf": "high",
                                     "record_end": st.record_end.isoformat() if st.record_end else None}})
    for s in structures.structures:
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [s.lon, s.lat]},
                      "properties": {"class": "structure", "id": s.structure_id,
                                     "crosses": s.crosses, "year_built": s.year_built,
                                     "condition": s.condition, "coord_conf": s.coord_conf.value,
                                     "segment_id": s.segment_id}})
    for g in seg.segments:
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [g.lon, g.lat]},
                      "properties": {"class": "segment-centroid", "id": g.segment_id,
                                     "name": g.name, "typology": g.typology,
                                     "coord_conf": g.coord_conf.value,
                                     "caveat": "approximation — orientation only, not for use of record"}})
    return {"type": "FeatureCollection",
            "properties": {"site_id": seg.site_id, "crs": "EPSG:4326",
                           "vertical_datum_note": "elevations NAVD88 when present",
                           "corridor_line": "TO_BE_FILLED — OSM way polyline pull queued",
                           "model_extraction_points": "TO_BE_FILLED — defined with CoSMoS Step 2"},
            "features": feats}
