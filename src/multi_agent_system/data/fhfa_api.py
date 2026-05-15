"""
fhfa_api.py - FHFA House Price Index API Integration for MAS

Provides programmatic access to Federal Housing Finance Agency data including:
- House Price Index (HPI) data
- Regional and state-level housing price trends

Data Provenance:
    Source: FHFA (https://www.fhfa.gov/DataTools/Downloads/Pages/House-Price-Index.aspx)
    Update Frequency: QUARTERLY (HPI updated quarterly)
    Access Level: PUBLIC
    Data Format: JSON

ADK/A2A Compatibility:
    - Exposed as ADK tool via decorator
    - Returns standardized result dict with enums
    - Registered in AgentCard for discoverability
"""
import logging
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

BASE_URL = "https://www.fhfa.gov/api/hpi"
_CACHE = SimpleCache(ttl=3600)  # 1-hour cache for FHFA data

# Metadata for AgentCard registration
FHFA_TOOL_METADATA = {
    "name": "fhfa_query",
    "description": "Query FHFA for house price index and housing market data",
    "domain": DataDomain.ECONOMIC,
    "update_frequency": DataUpdateFrequency.QUARTERLY,
    "access_level": DataAccessLevel.PUBLIC,
    "data_format": DataFormat.JSON,
}


class FHFAAPIError(Exception):
    """Custom exception for FHFA API errors."""
    pass


def get_fhfa_data(
    params: dict[str, Any] | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Fetch data from FHFA House Price Index API.

    Args:
        params: Query parameters (state, metro area, date range)
        use_cache: if True, use in-memory cache

    Returns:
        dict: Standardized result with the following fields:
            - status: DataLoadStatus (SUCCESS or ERROR)
            - data: The response data (if successful)
            - provenance: DataProvenance (API or STATIC for cached)
            - update_frequency: DataUpdateFrequency.QUARTERLY
            - data_format: DataFormat.JSON
            - access_level: DataAccessLevel.PUBLIC
            - domain: DataDomain.ECONOMIC
            - error_type: DataErrorType (if error)
            - error: str (error message if error)

    Example:
        >>> result = get_fhfa_data({'state': 'AL'})
        >>> if result["status"] == DataLoadStatus.SUCCESS:
        ...     print(result["data"])
    """
    key = f"fhfa:{sorted((params or {}).items())}"

    base_metadata = {
        "update_frequency": DataUpdateFrequency.QUARTERLY,
        "data_format": DataFormat.JSON,
        "access_level": DataAccessLevel.PUBLIC,
        "domain": DataDomain.ECONOMIC,
    }

    # Check cache first
    if use_cache:
        cached = _CACHE.get(key)
        if cached is not None:
            logger.info("FHFA cache hit")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": cached,
                "provenance": DataProvenance.STATIC,
                "error_type": None,
                "error": None,
                **base_metadata,
            }

    try:
        logger.info("FHFA API request")
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
        logger.error(f"FHFA API request failed: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.NETWORK,
            "error": f"FHFA API request failed: {e}",
            **base_metadata,
        }
    except Exception as e:
        logger.error(f"Unexpected error in FHFA query: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.UNKNOWN,
            "error": f"Unexpected error: {e}",
            **base_metadata,
        }


def get_state_hpi(state: str) -> dict[str, Any]:
    """
    Get House Price Index for a state.

    Args:
        state: Two-letter state code (e.g., 'AL' for Alabama)

    Returns:
        dict: Standardized result with HPI data
    """
    params = {"state": state.upper()}
    return get_fhfa_data(params)
