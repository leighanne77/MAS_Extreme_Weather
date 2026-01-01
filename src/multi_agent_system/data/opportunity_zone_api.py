"""
Opportunity Zone API Integration Module

This module provides functions to query the HUD ArcGIS REST API for Opportunity Zone (OZ) data.

API Reference:
- HUD ArcGIS REST API: https://opportunityzones.arcgis.com/arcgis/rest/services/OppZone/MapServer/0

Usage:
- get_opportunity_zones_by_state(state_abbr)
- get_opportunity_zone_by_tract(tract_id)

"""
import requests
from typing import List, Dict, Optional
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

HUD_OZ_API_URL = "https://opportunityzones.arcgis.com/arcgis/rest/services/OppZone/MapServer/0/query"


def query_opportunity_zones(where: str = "1=1", out_fields: str = "*", return_geometry: bool = True, result_offset: int = 0, result_record_count: int = 1000, spatial_rel: str = None, order_by_fields: str = None) -> List[Dict]:
    """
    Generic query function for Opportunity Zones using the HUD ArcGIS REST API.
    Args:
        where (str): SQL-like where clause for filtering.
        out_fields (str): Comma-separated list of fields to return.
        return_geometry (bool): Whether to return geometry.
        result_offset (int): Record offset for pagination.
        result_record_count (int): Number of records to return (max 1000 per API docs).
        spatial_rel (str): Optional spatial relationship (e.g., 'esriSpatialRelIntersects').
        order_by_fields (str): Optional order by fields.
    Returns:
        List[Dict]: List of Opportunity Zone features (GeoJSON-like dicts)
    """
    params = {
        "where": where,
        "outFields": out_fields,
        "f": "json",
        "returnGeometry": return_geometry,
        "resultOffset": result_offset,
        "resultRecordCount": result_record_count
    }
    if spatial_rel:
        params["spatialRel"] = spatial_rel
    if order_by_fields:
        params["orderByFields"] = order_by_fields
    try:
        resp = requests.get(HUD_OZ_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("features", [])
    except Exception as e:
        logger.error(f"OZ API query failed: {e}", exc_info=True)
        return []


def get_opportunity_zones_by_state(state_abbr: str) -> List[Dict]:
    """
    Query the HUD ArcGIS REST API for all Opportunity Zones in a given state.
    Args:
        state_abbr (str): Two-letter state abbreviation (e.g., 'AL' for Alabama)
    Returns:
        List[Dict]: List of Opportunity Zone features (GeoJSON-like dicts)
    """
    where = f"ST_ABBREV='{state_abbr.upper()}'"
    return query_opportunity_zones(where=where)


def get_opportunity_zone_by_tract(tract_id: str) -> Optional[Dict]:
    """
    Query the HUD ArcGIS REST API for a specific Opportunity Zone by Census Tract GEOID.
    Args:
        tract_id (str): Census Tract GEOID (11-digit string)
    Returns:
        Optional[Dict]: Opportunity Zone feature dict, or None if not found
    """
    where = f"TRACTCE10='{tract_id}'"
    results = query_opportunity_zones(where=where)
    return results[0] if results else None


def get_opportunity_zones_by_county(county_fips: str) -> List[Dict]:
    """
    Query the HUD ArcGIS REST API for all Opportunity Zones in a given county (by FIPS code).
    Args:
        county_fips (str): 5-digit county FIPS code (state+county)
    Returns:
        List[Dict]: List of Opportunity Zone features
    """
    where = f"COUNTYFP10='{county_fips}'"
    return query_opportunity_zones(where=where)


def get_opportunity_zones_custom(
    state_abbr: str = None,
    county_fips: str = None,
    min_area: float = None,
    order_by: str = None,
    limit: int = 1000
) -> List[Dict]:
    """
    Flexible query for Opportunity Zones with multiple filters.
    Args:
        state_abbr (str): Two-letter state abbreviation.
        county_fips (str): 5-digit county FIPS code.
        min_area (float): Minimum area (in sq meters) for OZ polygon.
        order_by (str): Field(s) to order results by.
        limit (int): Max number of results.
    Returns:
        List[Dict]: List of Opportunity Zone features.
    """
    where_clauses = []
    if state_abbr:
        where_clauses.append(f"ST_ABBREV='{state_abbr.upper()}'")
    if county_fips:
        where_clauses.append(f"COUNTYFP10='{county_fips}'")
    if min_area:
        where_clauses.append(f"Shape_Area>{min_area}")
    where = " AND ".join(where_clauses) if where_clauses else "1=1"
    return query_opportunity_zones(where=where, order_by_fields=order_by, result_record_count=limit)


# Example usage (for testing):
if __name__ == "__main__":
    # Get all OZs in Alabama
    alabama_ozs = get_opportunity_zones_by_state("AL")
    print(f"Found {len(alabama_ozs)} Opportunity Zones in Alabama.")
    # Get OZ by tract
    example_tract = "01003010100"  # Replace with a real tract GEOID
    oz = get_opportunity_zone_by_tract(example_tract)
    if oz:
        print(f"OZ found for tract {example_tract}: {oz['attributes']}")
    else:
        print(f"No OZ found for tract {example_tract}.")

"""
Module reference for agents:
- Used by: reference_data_agent, due_diligence_agent, query_refinement_agent, progress_display_agent
- Provides: Direct [API] access to live Opportunity Zone data (HUD ArcGIS REST API)
- See also: data_loader.py for unified static/live OZ data access
"""
