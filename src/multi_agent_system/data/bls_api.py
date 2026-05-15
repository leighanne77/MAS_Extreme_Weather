"""
bls_api.py - Bureau of Labor Statistics Public Data API Integration for MAS

Provides programmatic access to BLS employment, wages, and labor market data.
- Uses requests for HTTP calls
- Input validation and error handling
- Simple in-memory cache for repeated queries

Data Provenance:
    Source: Bureau of Labor Statistics (https://www.bls.gov/developers/)
    Update Frequency: MONTHLY (most series updated monthly)
    Access Level: PUBLIC (API key recommended for higher rate limits)
    Data Format: JSON

ADK/A2A Compatibility:
    - Exposed as ADK tool via decorator
    - Returns standardized result dict with enums
    - Registered in AgentCard for discoverability
"""
import logging
import os
import time
from typing import Any, List

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

BLS_API_KEY = os.getenv("BLS_API_KEY")
BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
_CACHE = SimpleCache(ttl=3600)  # 1-hour cache for BLS data

# Metadata for AgentCard registration
BLS_TOOL_METADATA = {
    "name": "bls_query",
    "description": "Query Bureau of Labor Statistics for employment and wage data",
    "domain": DataDomain.ECONOMIC,
    "update_frequency": DataUpdateFrequency.MONTHLY,
    "access_level": DataAccessLevel.PUBLIC,
    "data_format": DataFormat.JSON,
}


class BLSAPIError(Exception):
    """Custom exception for BLS API errors."""
    pass


def get_bls_data(
    series_ids: List[str],
    start_year: str,
    end_year: str,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Fetch data from BLS Public Data API.

    Args:
        series_ids: List of BLS series IDs (e.g., ['LAUCN010010000000003', 'LAUCN010010000000004'])
        start_year: Start year (e.g., '2020')
        end_year: End year (e.g., '2024')
        use_cache: if True, use in-memory cache

    Returns:
        dict: Standardized result with the following fields:
            - status: DataLoadStatus (SUCCESS or ERROR)
            - data: The response data (if successful)
            - provenance: DataProvenance (API or STATIC for cached)
            - update_frequency: DataUpdateFrequency.MONTHLY
            - data_format: DataFormat.JSON
            - access_level: DataAccessLevel.PUBLIC
            - domain: DataDomain.ECONOMIC
            - error_type: DataErrorType (if error)
            - error: str (error message if error)

    Example:
        >>> result = get_bls_data(['LAUCN010010000000003'], '2020', '2024')
        >>> if result["status"] == DataLoadStatus.SUCCESS:
        ...     print(result["data"])
    """
    headers = {"Content-type": "application/json"}
    key = f"bls:{sorted(series_ids)}:{start_year}:{end_year}"

    base_metadata = {
        "update_frequency": DataUpdateFrequency.MONTHLY,
        "data_format": DataFormat.JSON,
        "access_level": DataAccessLevel.PUBLIC,
        "domain": DataDomain.ECONOMIC,
    }

    # Check cache first
    if use_cache:
        cached = _CACHE.get(key)
        if cached is not None:
            logger.info(f"BLS cache hit for series {series_ids}")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": cached,
                "provenance": DataProvenance.STATIC,
                "error_type": None,
                "error": None,
                **base_metadata,
            }

    data = {
        "seriesid": series_ids,
        "startyear": start_year,
        "endyear": end_year,
        "registrationkey": BLS_API_KEY,
    }

    try:
        logger.info(f"BLS API request for series {series_ids}")
        resp = requests.post(BASE_URL, json=data, headers=headers, timeout=20)
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
        logger.error(f"BLS API request failed: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.NETWORK,
            "error": f"BLS API request failed: {e}",
            **base_metadata,
        }
    except Exception as e:
        logger.error(f"Unexpected error in BLS query: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.UNKNOWN,
            "error": f"Unexpected error: {e}",
            **base_metadata,
        }


def get_unemployment_data(
    state_fips: str,
    county_fips: str,
    start_year: str,
    end_year: str,
) -> dict[str, Any]:
    """
    Get local area unemployment statistics.

    Args:
        state_fips: State FIPS code (2 digits)
        county_fips: County FIPS code (3 digits)
        start_year: Start year
        end_year: End year

    Returns:
        dict: Standardized result with unemployment data
    """
    # LAUS series ID format: LAUCN{state}{county}0000000003 (unemployment rate)
    series_id = f"LAUCN{state_fips}{county_fips}0000000003"
    return get_bls_data([series_id], start_year, end_year)
