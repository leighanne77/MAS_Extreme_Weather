"""
eia_api.py - U.S. Energy Information Administration Open Data API Integration for MAS

Provides programmatic access to EIA energy data including:
- Electricity generation and consumption
- Natural gas prices and storage
- Petroleum and renewable energy data

Data Provenance:
    Source: EIA Open Data (https://www.eia.gov/opendata/)
    Update Frequency: VARIES (hourly to annual depending on series)
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

EIA_API_KEY = os.getenv("EIA_API_KEY")
BASE_URL = "https://api.eia.gov/series/"
_CACHE = SimpleCache(ttl=3600)  # 1-hour cache for EIA data

# Metadata for AgentCard registration
EIA_TOOL_METADATA = {
    "name": "eia_query",
    "description": "Query EIA for energy production, consumption, and pricing data",
    "domain": DataDomain.ECONOMIC,
    "update_frequency": DataUpdateFrequency.DAILY,
    "access_level": DataAccessLevel.PUBLIC,
    "data_format": DataFormat.JSON,
}


class EIAAPIError(Exception):
    """Custom exception for EIA API errors."""
    pass


def get_eia_data(
    series_id: str,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Fetch data from EIA Open Data API.

    Args:
        series_id: EIA series ID (e.g., 'PET.RWTC.D' for WTI crude oil price)
        use_cache: if True, use in-memory cache

    Returns:
        dict: Standardized result with the following fields:
            - status: DataLoadStatus (SUCCESS or ERROR)
            - data: The response data (if successful)
            - provenance: DataProvenance (API or STATIC for cached)
            - update_frequency: DataUpdateFrequency.DAILY
            - data_format: DataFormat.JSON
            - access_level: DataAccessLevel.PUBLIC
            - domain: DataDomain.ECONOMIC
            - error_type: DataErrorType (if error)
            - error: str (error message if error)

    Example:
        >>> result = get_eia_data('PET.RWTC.D')
        >>> if result["status"] == DataLoadStatus.SUCCESS:
        ...     print(result["data"])
    """
    key = f"eia:{series_id}"

    base_metadata = {
        "update_frequency": DataUpdateFrequency.DAILY,
        "data_format": DataFormat.JSON,
        "access_level": DataAccessLevel.PUBLIC,
        "domain": DataDomain.ECONOMIC,
    }

    # Check cache first
    if use_cache:
        cached = _CACHE.get(key)
        if cached is not None:
            logger.info(f"EIA cache hit for {series_id}")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": cached,
                "provenance": DataProvenance.STATIC,
                "error_type": None,
                "error": None,
                **base_metadata,
            }

    params = {"api_key": EIA_API_KEY, "series_id": series_id}

    try:
        logger.info(f"EIA API request for series {series_id}")
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
        logger.error(f"EIA API request failed: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.NETWORK,
            "error": f"EIA API request failed: {e}",
            **base_metadata,
        }
    except Exception as e:
        logger.error(f"Unexpected error in EIA query: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.UNKNOWN,
            "error": f"Unexpected error: {e}",
            **base_metadata,
        }


def get_electricity_price(state: str) -> dict[str, Any]:
    """
    Get average retail electricity price for a state.

    Args:
        state: Two-letter state code (e.g., 'AL' for Alabama)

    Returns:
        dict: Standardized result with electricity price data
    """
    # ELEC.PRICE.{STATE}-ALL.A - Average retail price, all sectors
    series_id = f"ELEC.PRICE.{state.upper()}-ALL.A"
    return get_eia_data(series_id)
