"""
OpenStreetMap Overpass API Integration
Docs: https://wiki.openstreetmap.org/wiki/Overpass_API
"""
import requests
import logging

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def get_osm_data(query: str) -> dict:
    """
    Fetch data from OpenStreetMap Overpass API.
    Args:
        query (str): Overpass QL query string
    Returns:
        dict: API response
    """
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"OSM API error: {e}", exc_info=True)
        return {}
