"""
census_api.py - Census Bureau Data API Integration for MAS

Provides programmatic access to US Census Bureau data including:
- American Community Survey (ACS)
- Decennial Census
- Economic Census

Data Provenance:
    Source: US Census Bureau (https://www.census.gov/data/developers/data-sets.html)
    Update Frequency: ANNUAL (ACS 1-year, 5-year estimates)
    Access Level: PUBLIC
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

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
BASE_URL = "https://api.census.gov/data/"
_CACHE = SimpleCache(ttl=3600)  # 1-hour cache for Census data

# Metadata for AgentCard registration
CENSUS_TOOL_METADATA = {
    "name": "census_query",
    "description": "Query US Census Bureau for demographic and economic data",
    "domain": DataDomain.ECONOMIC,
    "update_frequency": DataUpdateFrequency.ANNUAL,
    "access_level": DataAccessLevel.PUBLIC,
    "data_format": DataFormat.JSON,
}


class CensusAPIError(Exception):
    """Custom exception for Census API errors."""
    pass


def get_census_data(
    year: str,
    dataset: str,
    params: dict[str, Any] | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Fetch data from Census Bureau API.

    Args:
        year: Data year (e.g., '2020')
        dataset: Dataset name (e.g., 'acs/acs5', 'acs/acs1', 'dec/pl')
        params: Query parameters (get, for, in clauses)
        use_cache: if True, use in-memory cache

    Returns:
        dict: Standardized result with the following fields:
            - status: DataLoadStatus (SUCCESS or ERROR)
            - data: The response data (if successful)
            - provenance: DataProvenance (API or STATIC for cached)
            - update_frequency: DataUpdateFrequency.ANNUAL
            - data_format: DataFormat.JSON
            - access_level: DataAccessLevel.PUBLIC
            - domain: DataDomain.ECONOMIC
            - error_type: DataErrorType (if error)
            - error: str (error message if error)

    Example:
        >>> result = get_census_data('2020', 'acs/acs5', {'get': 'B01001_001E', 'for': 'county:*'})
        >>> if result["status"] == DataLoadStatus.SUCCESS:
        ...     print(result["data"])
    """
    url = f"{BASE_URL}{year}/{dataset}"
    params = params.copy() if params else {}
    params["key"] = CENSUS_API_KEY
    key = f"census:{year}:{dataset}:{sorted(params.items())}"

    base_metadata = {
        "update_frequency": DataUpdateFrequency.ANNUAL,
        "data_format": DataFormat.JSON,
        "access_level": DataAccessLevel.PUBLIC,
        "domain": DataDomain.ECONOMIC,
    }

    # Check cache first
    if use_cache:
        cached = _CACHE.get(key)
        if cached is not None:
            logger.info(f"Census cache hit for {year}/{dataset}")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": cached,
                "provenance": DataProvenance.STATIC,
                "error_type": None,
                "error": None,
                **base_metadata,
            }

    try:
        logger.info(f"Census API request to {year}/{dataset}")
        resp = requests.get(url, params=params, timeout=20)
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
        logger.error(f"Census API request failed: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.NETWORK,
            "error": f"Census API request failed: {e}",
            **base_metadata,
        }
    except Exception as e:
        logger.error(f"Unexpected error in Census query: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.UNKNOWN,
            "error": f"Unexpected error: {e}",
            **base_metadata,
        }


def get_acs_population(
    year: str,
    state_fips: str,
    county_fips: str | None = None,
) -> dict[str, Any]:
    """
    Get American Community Survey population data.

    Args:
        year: Data year
        state_fips: State FIPS code
        county_fips: County FIPS code (optional, for county-level data)

    Returns:
        dict: Standardized result with population data
    """
    params = {"get": "B01001_001E,NAME"}
    if county_fips:
        params["for"] = f"county:{county_fips}"
        params["in"] = f"state:{state_fips}"
    else:
        params["for"] = f"state:{state_fips}"

    return get_census_data(year, "acs/acs5", params)
