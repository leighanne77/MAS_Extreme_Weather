"""
openfema_api.py - OpenFEMA API Integration for MAS

Provides programmatic access to FEMA disaster data including:
- Disaster declarations
- Hazard mitigation projects
- Individual and public assistance data

Data Provenance:
    Source: FEMA OpenFEMA (https://www.fema.gov/about/openfema/data-sets)
    Update Frequency: DAILY (disaster declarations updated frequently)
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

BASE_URL = "https://www.fema.gov/api/open/v2/"
_CACHE = SimpleCache(ttl=1800)  # 30-minute cache for FEMA data

# Metadata for AgentCard registration
OPENFEMA_TOOL_METADATA = {
    "name": "openfema_query",
    "description": "Query OpenFEMA for disaster declarations and hazard data",
    "domain": DataDomain.ENVIRONMENTAL,
    "update_frequency": DataUpdateFrequency.DAILY,
    "access_level": DataAccessLevel.PUBLIC,
    "data_format": DataFormat.JSON,
}


class OpenFEMAAPIError(Exception):
    """Custom exception for OpenFEMA API errors."""
    pass


def get_openfema_data(
    dataset: str,
    params: dict[str, Any] | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Fetch data from OpenFEMA API.

    Args:
        dataset: Dataset name (e.g., 'DisasterDeclarationsSummaries', 
                 'HazardMitigationAssistanceProjects', 'FemaWebDisasterDeclarations')
        params: Query parameters (filters, pagination)
        use_cache: if True, use in-memory cache

    Returns:
        dict: Standardized result with the following fields:
            - status: DataLoadStatus (SUCCESS or ERROR)
            - data: The response data (if successful)
            - provenance: DataProvenance (API or STATIC for cached)
            - update_frequency: DataUpdateFrequency.DAILY
            - data_format: DataFormat.JSON
            - access_level: DataAccessLevel.PUBLIC
            - domain: DataDomain.ENVIRONMENTAL
            - error_type: DataErrorType (if error)
            - error: str (error message if error)

    Example:
        >>> result = get_openfema_data('DisasterDeclarationsSummaries', {'$filter': "state eq 'AL'"})
        >>> if result["status"] == DataLoadStatus.SUCCESS:
        ...     print(result["data"])
    """
    url = BASE_URL + dataset
    key = f"openfema:{dataset}:{sorted((params or {}).items())}"

    base_metadata = {
        "update_frequency": DataUpdateFrequency.DAILY,
        "data_format": DataFormat.JSON,
        "access_level": DataAccessLevel.PUBLIC,
        "domain": DataDomain.ENVIRONMENTAL,
    }

    # Check cache first
    if use_cache:
        cached = _CACHE.get(key)
        if cached is not None:
            logger.info(f"OpenFEMA cache hit for {dataset}")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": cached,
                "provenance": DataProvenance.STATIC,
                "error_type": None,
                "error": None,
                **base_metadata,
            }

    try:
        logger.info(f"OpenFEMA API request to {dataset}")
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
        logger.error(f"OpenFEMA API request failed: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.NETWORK,
            "error": f"OpenFEMA API request failed: {e}",
            **base_metadata,
        }
    except Exception as e:
        logger.error(f"Unexpected error in OpenFEMA query: {e}")
        return {
            "status": DataLoadStatus.ERROR,
            "data": None,
            "provenance": DataProvenance.API,
            "error_type": DataErrorType.UNKNOWN,
            "error": f"Unexpected error: {e}",
            **base_metadata,
        }


def get_disaster_declarations(
    state: str | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    """
    Get FEMA disaster declarations.

    Args:
        state: Two-letter state code (optional)
        year: Year to filter by (optional)

    Returns:
        dict: Standardized result with disaster declarations
    """
    params = {}
    filters = []
    if state:
        filters.append(f"state eq '{state.upper()}'")
    if year:
        filters.append(f"fyDeclared eq {year}")
    if filters:
        params["$filter"] = " and ".join(filters)

    return get_openfema_data("DisasterDeclarationsSummaries", params)
