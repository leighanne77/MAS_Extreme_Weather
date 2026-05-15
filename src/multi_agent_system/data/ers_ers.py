"""
ers_ers.py - USDA Economic Research Service API integration for MAS

Provides programmatic access to farm income, costs, and financial indicators from the ERS.
- Uses requests for HTTP calls
- Input validation and error handling
- Security best practices
- Simple in-memory cache for repeated queries

Data Provenance:
    Source: USDA Economic Research Service (https://www.ers.usda.gov/)
    Update Frequency: ANNUAL (farm income data updated yearly)
    Access Level: PUBLIC
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

from .cache_utils import SimpleCache

logger = logging.getLogger(__name__)

ERS_API_BASE = "https://api.ers.usda.gov/"
_CACHE = SimpleCache(ttl=300)

# Metadata for AgentCard registration
ERS_TOOL_METADATA = {
    "name": "ers_query",
    "description": "Query USDA Economic Research Service for farm income and financial indicators",
    "domain": DataDomain.ECONOMIC,
    "update_frequency": DataUpdateFrequency.ANNUAL,
    "access_level": DataAccessLevel.PUBLIC,
    "data_format": DataFormat.JSON,
}


class ERSAPIError(Exception):
    """Custom exception for ERS API errors."""
    pass


def ers_query(endpoint: str, params: dict[str, Any], use_cache: bool = True) -> dict[str, Any]:
    """
    Query the ERS API (if/when available).

    Args:
        endpoint: API endpoint (e.g., 'farm-income')
        params: dict of query parameters
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
        >>> result = ers_query("farm-income", {"year": 2023})
        >>> if result["status"] == DataLoadStatus.SUCCESS:
        ...     print(result["data"])
    """
    url = ERS_API_BASE + endpoint
    key = f"{endpoint}:{sorted(params.items())}"
    
    base_metadata = {
        "update_frequency": DataUpdateFrequency.ANNUAL,
        "data_format": DataFormat.JSON,
        "access_level": DataAccessLevel.PUBLIC,
        "domain": DataDomain.ECONOMIC,
    }
    
    if use_cache:
        cached = _CACHE.get(key)
        if cached is not None:
            logger.info(f"ERS cache hit for {endpoint}")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": cached,
                "provenance": DataProvenance.STATIC,
                "error_type": None,
                "error": None,
                **base_metadata,
            }
    
    try:
        logger.info(f"ERS API request to {endpoint}")
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if use_cache:
            _CACHE.set(key, data)
        return {
            "status": DataLoadStatus.SUCCESS,
            "data": data,
            "provenance": DataProvenance.API,
            "error_type": None,
            "error": None,
            **base_metadata,
        }
    except requests.RequestException as e:
        logger.error(f"ERS API request failed: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.NETWORK,
            "error": f"ERS API request failed: {e}",
            **base_metadata,
        }
    except Exception as e:
        logger.error(f"Unexpected error in ERS query: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.UNKNOWN,
            "error": f"Unexpected error: {e}",
            **base_metadata,
        }


def get_farm_income(year: int) -> dict[str, Any]:
    params = {"year": year}
    return ers_query("farm-income", params)
