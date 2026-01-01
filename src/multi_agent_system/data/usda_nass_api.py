"""
usda_nass_api.py - USDA NASS Quick Stats API Integration for Pythia

Provides programmatic access to agricultural statistics via the Quick Stats API.
- Crop yields and production data
- Livestock counts and values
- Agricultural economics data

Data Provenance:
    Source: USDA NASS Quick Stats (https://quickstats.nass.usda.gov/api/)
    Update Frequency: WEEKLY (during growing season)
    Access Level: PUBLIC (API key required)
    Data Format: JSON

ADK/A2A Compatibility:
    - Exposed as ADK tool via decorator
    - Returns standardized result dict with enums
    - Registered in AgentCard for discoverability
"""
import logging
import os
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

from .cache_utils import SimpleCache

logger = logging.getLogger(__name__)

QUICKSTATS_API_KEY = os.getenv("QUICKSTATS_API_KEY")
BASE_URL = "https://quickstats.nass.usda.gov/api/api_GET/"
_CACHE = SimpleCache(ttl=1800)  # 30-minute cache for NASS data

# Metadata for AgentCard registration
USDA_NASS_TOOL_METADATA = {
    "name": "usda_nass_query",
    "description": "Query USDA NASS Quick Stats for crop yields and agricultural data",
    "domain": DataDomain.AGRICULTURE,
    "update_frequency": DataUpdateFrequency.WEEKLY,
    "access_level": DataAccessLevel.PUBLIC,
    "data_format": DataFormat.JSON,
}


class USDNASSAPIError(Exception):
    """Custom exception for USDA NASS API errors."""
    pass


def get_nass_data(
    params: dict[str, Any],
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Fetch data from USDA NASS Quick Stats API.

    Args:
        params: Query parameters (commodity_desc, year, state_alpha, etc.)
        use_cache: if True, use in-memory cache

    Returns:
        dict: Standardized result with the following fields:
            - status: DataLoadStatus (SUCCESS or ERROR)
            - data: The response data (if successful)
            - provenance: DataProvenance (API or STATIC for cached)
            - update_frequency: DataUpdateFrequency.WEEKLY
            - data_format: DataFormat.JSON
            - access_level: DataAccessLevel.PUBLIC
            - domain: DataDomain.AGRICULTURE
            - error_type: DataErrorType (if error)
            - error: str (error message if error)

    Example:
        >>> result = get_nass_data({'commodity_desc': 'CORN', 'year': 2023})
        >>> if result["status"] == DataLoadStatus.SUCCESS:
        ...     print(result["data"])
    """
    params = params.copy()
    params["key"] = QUICKSTATS_API_KEY
    key = f"nass:{sorted(params.items())}"

    base_metadata = {
        "update_frequency": DataUpdateFrequency.WEEKLY,
        "data_format": DataFormat.JSON,
        "access_level": DataAccessLevel.PUBLIC,
        "domain": DataDomain.AGRICULTURE,
    }

    # Check cache first
    if use_cache:
        cached = _CACHE.get(key)
        if cached is not None:
            logger.info("USDA NASS cache hit")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": cached,
                "provenance": DataProvenance.STATIC,
                "error_type": None,
                "error": None,
                **base_metadata,
            }

    try:
        logger.info(f"USDA NASS API request with params: {params}")
        resp = requests.get(BASE_URL, params=params, timeout=20)
        resp.raise_for_status()
        result_data = resp.json()

        if use_cache:
            _CACHE.set(key, result_data)

        return {
            "status": DataLoadStatus.SUCCESS,
            "data": result_data,
            "provenance": DataProvenance.API,
            "error_type": None,
            "error": None,
            **base_metadata,
        }
    except requests.RequestException as e:
        logger.error(f"USDA NASS API request failed: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.NETWORK,
            "error": f"USDA NASS API request failed: {e}",
            **base_metadata,
        }
    except Exception as e:
        logger.error(f"Unexpected error in USDA NASS query: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.UNKNOWN,
            "error": f"Unexpected error: {e}",
            **base_metadata,
        }


def get_crop_production(
    commodity: str,
    year: int,
    state: str | None = None,
) -> dict[str, Any]:
    """
    Get crop production data.

    Args:
        commodity: Commodity name (e.g., 'CORN', 'WHEAT', 'SOYBEANS')
        year: Year to query
        state: Two-letter state code (optional)

    Returns:
        dict: Standardized result with crop production data
    """
    params = {
        "commodity_desc": commodity.upper(),
        "year": year,
        "statisticcat_desc": "PRODUCTION",
    }
    if state:
        params["state_alpha"] = state.upper()

    return get_nass_data(params)
