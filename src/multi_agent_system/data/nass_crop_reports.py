"""
nass_crop_reports.py - USDA NASS Crop Reports API integration for Pythia

Provides programmatic access to yield data and production forecasts from the NASS Quick Stats API.
- Uses requests for HTTP calls
- Input validation and error handling
- Security best practices
- Simple in-memory cache for repeated queries

Data Provenance:
    Source: USDA NASS Quick Stats API (https://quickstats.nass.usda.gov/api/)
    Update Frequency: WEEKLY (crop reports updated weekly during growing season)
    Access Level: PUBLIC (requires API key)
    Data Format: JSON

ADK/A2A Compatibility:
    - Exposed as ADK tool via decorator
    - Returns standardized result dict with enums
    - Registered in AgentCard for discoverability
"""
import logging
import time
from typing import Any

import requests

from enums import (
    DataAccessLevel,
    DataDomain,
    DataErrorType,
    DataFormat,
    DataLoadStatus,
    DataProvenance,
    DataUpdateFrequency,
)

logger = logging.getLogger(__name__)

NASS_API_BASE = "https://quickstats.nass.usda.gov/api/api_GET/"
_CACHE: dict[str, tuple[float, Any]] = {}
_CACHE_TTL = 300

# Metadata for AgentCard registration
NASS_TOOL_METADATA = {
    "name": "nass_query",
    "description": "Query USDA NASS Quick Stats API for crop yield and production data",
    "domain": DataDomain.AGRICULTURE,
    "update_frequency": DataUpdateFrequency.WEEKLY,
    "access_level": DataAccessLevel.PUBLIC,
    "data_format": DataFormat.JSON,
}


class NASSAPIError(Exception):
    """Custom exception for NASS API errors."""
    pass


def _cache_get(key: str) -> Any | None:
    """Get value from cache if not expired."""
    entry = _CACHE.get(key)
    if entry:
        ts, val = entry
        if time.time() - ts < _CACHE_TTL:
            return val
        else:
            del _CACHE[key]
    return None


def _cache_set(key: str, value: Any) -> None:
    """Set value in cache with timestamp."""
    _CACHE[key] = (time.time(), value)


def nass_query(params: dict[str, Any], use_cache: bool = True) -> dict[str, Any]:
    """
    Query the NASS Quick Stats API.

    Args:
        params: dict of query parameters (must include 'key' for API key)
        use_cache: if True, use in-memory cache

    Returns:
        dict: Standardized result with the following fields:
            - status: DataLoadStatus (SUCCESS or ERROR)
            - data: The response data (if successful)
            - provenance: DataProvenance (API or STATIC for cached)
            - update_frequency: DataUpdateFrequency
            - data_format: DataFormat
            - access_level: DataAccessLevel
            - domain: DataDomain
            - error_type: DataErrorType (if error)
            - error: str (error message if error)

    Example:
        >>> result = nass_query({"key": "YOUR_API_KEY", "commodity_desc": "CORN", "year": 2023})
        >>> if result["status"] == DataLoadStatus.SUCCESS:
        ...     print(result["data"])
    """
    base_metadata = {
        "update_frequency": DataUpdateFrequency.WEEKLY,
        "data_format": DataFormat.JSON,
        "access_level": DataAccessLevel.PUBLIC,
        "domain": DataDomain.AGRICULTURE,
    }
    
    if "key" not in params:
        logger.error("NASS API key not provided")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.VALIDATION,
            "error": "API key ('key') is required for NASS Quick Stats API.",
            **base_metadata,
        }
    
    cache_key = str(sorted(params.items()))
    if use_cache:
        cached = _cache_get(cache_key)
        if cached is not None:
            logger.info("NASS cache hit")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": cached,
                "provenance": DataProvenance.STATIC,
                "error_type": None,
                "error": None,
                **base_metadata,
            }
    
    try:
        logger.info("NASS API request")
        resp = requests.get(NASS_API_BASE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        _cache_set(cache_key, data)
        return {
            "status": DataLoadStatus.SUCCESS,
            "data": data,
            "provenance": DataProvenance.API,
            "error_type": None,
            "error": None,
            **base_metadata,
        }
    except requests.RequestException as e:
        logger.error(f"NASS API request failed: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.NETWORK,
            "error": f"NASS API request failed: {e}",
            **base_metadata,
        }
    except Exception as e:
        logger.error(f"Unexpected error in NASS query: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.UNKNOWN,
            "error": f"Unexpected error: {e}",
            **base_metadata,
        }


def get_crop_yield(api_key: str, commodity_desc: str, year: int, state_alpha: str | None = None) -> dict[str, Any]:
    params = {
        "key": api_key,
        "commodity_desc": commodity_desc,
        "year": year,
        "format": "JSON"
    }
    if state_alpha:
        params["state_alpha"] = state_alpha
    return nass_query(params)
