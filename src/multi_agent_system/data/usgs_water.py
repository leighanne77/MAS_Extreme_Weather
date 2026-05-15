"""
usgs_water.py - USGS Water Services API data provider for MAS multi-agent system

Features:
- Centralizes all USGS API logic (modular, maintainable)
- Input validation and error handling
- Uses requests with timeouts
- Security best practices (no sensitive logging, safe query interface)
- Optional in-memory caching for repeated queries
"""
import requests
import time
from typing import Dict, Any, Optional
from .cache_utils import SimpleCache

USGS_BASE_URL = "https://waterservices.usgs.gov/nwis/"

class USGSWaterAPIError(Exception):
    pass

def _validate_params(params: Dict[str, Any]) -> None:
    # Only allow known safe parameters
    allowed = {"format", "sites", "siteType", "parameterCd", "startDT", "endDT", "stateCd", "countyCd"}
    for k in params:
        if k not in allowed:
            raise ValueError(f"Invalid parameter: {k}")
    # Example: require 'format' and 'sites' or 'stateCd'
    if "format" not in params:
        raise ValueError("'format' parameter is required (e.g., 'json')")
    if not ("sites" in params or "stateCd" in params):
        raise ValueError("Either 'sites' or 'stateCd' parameter is required.")

_CACHE = SimpleCache(ttl=300)

def usgs_water_query(service: str, params: Dict[str, Any], use_cache: bool = True) -> Any:
    """
    Query the USGS Water Services API.
    service: e.g., 'iv' (instantaneous values), 'dv' (daily values), 'site', etc.
    params: dict of query parameters (see USGS API docs)
    use_cache: if True, use in-memory cache
    Returns: parsed JSON response
    Raises: USGSWaterAPIError on error
    """
    _validate_params(params)
    url = f"{USGS_BASE_URL}{service}/"
    # Build a canonical cache key
    key = f"{service}:{sorted(params.items())}"
    if use_cache:
        cached = _CACHE.get(key)
        if cached is not None:
            return cached
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        if params.get("format") == "json":
            data = resp.json()
        else:
            data = resp.text
        if use_cache:
            _CACHE.set(key, data)
        return data
    except requests.RequestException as e:
        raise USGSWaterAPIError(f"USGS API request failed: {e}")
    except Exception as e:
        raise USGSWaterAPIError(f"Unexpected error: {e}")

# Example safe query interface

def get_site_instantaneous(site_id: str, parameterCd: str = "00060", startDT: Optional[str] = None, endDT: Optional[str] = None) -> Any:
    """
    Get instantaneous values (e.g., streamflow) for a USGS site.
    - site_id: USGS site code
    - parameterCd: USGS parameter code (default: 00060 = discharge)
    - startDT, endDT: ISO date strings (optional)
    Returns: JSON response
    """
    params = {
        "format": "json",
        "sites": site_id,
        "parameterCd": parameterCd
    }
    if startDT:
        params["startDT"] = startDT
    if endDT:
        params["endDT"] = endDT
    return usgs_water_query("iv", params)

# Add more safe query functions as needed
