"""
openet_api.py - OpenET API Integration for MAS Multi-Agent System

Provides programmatic access to OpenET evapotranspiration (ET) data for:
- Water management and irrigation optimization
- Agricultural water use analysis
- Drought monitoring and assessment

Data Provenance:
    Source: OpenET (https://etdata.org/api-info/)
    Update Frequency: DAILY (satellite-derived ET data)
    Access Level: RESTRICTED (requires API key)
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

_CACHE = SimpleCache(ttl=3600)  # 1-hour cache for OpenET data

# Metadata for AgentCard registration
OPENET_TOOL_METADATA = {
    "name": "openet_query",
    "description": "Query OpenET for evapotranspiration and water use data",
    "domain": DataDomain.WATER,
    "update_frequency": DataUpdateFrequency.DAILY,
    "access_level": DataAccessLevel.RESTRICTED,
    "data_format": DataFormat.JSON,
}


class OpenETAPIError(Exception):
    """Custom exception for OpenET API errors."""
    pass


class OpenETDataSource:
    """
    OpenET Data Source for evapotranspiration data.
    
    Provides access to satellite-derived ET data for water management
    and agricultural analytics.
    """
    
    def __init__(self):
        """Initialize OpenET data source with API key from environment."""
        self.api_key = os.getenv("OPENET_API_KEY")
        if not self.api_key:
            logger.warning("OPENET_API_KEY not found in environment. OpenET API calls will fail.")
        # Updated base URL to new OpenET API endpoint
        self.base_url = "https://etdata.org/api/"  # TODO: Confirm correct endpoint path per API docs

    def get_et(
        self,
        lon: float,
        lat: float,
        start_date: str,
        end_date: str,
        source: str = "ensemble",
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Retrieve evapotranspiration data for a given point and date range.

        Args:
            lon: Longitude
            lat: Latitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            source: Data source (default: 'ensemble')
            use_cache: if True, use in-memory cache

        Returns:
            dict: Standardized result with the following fields:
                - status: DataLoadStatus (SUCCESS or ERROR)
                - data: The response data (if successful)
                - provenance: DataProvenance (API or STATIC for cached)
                - update_frequency: DataUpdateFrequency.DAILY
                - data_format: DataFormat.JSON
                - access_level: DataAccessLevel.RESTRICTED
                - domain: DataDomain.WATER
                - error_type: DataErrorType (if error)
                - error: str (error message if error)

        Example:
            >>> source = OpenETDataSource()
            >>> result = source.get_et(-120.5, 38.5, '2023-01-01', '2023-12-31')
            >>> if result["status"] == DataLoadStatus.SUCCESS:
            ...     print(result["data"])
        """
        base_metadata = {
            "update_frequency": DataUpdateFrequency.DAILY,
            "data_format": DataFormat.JSON,
            "access_level": DataAccessLevel.RESTRICTED,
            "domain": DataDomain.WATER,
        }

        if not self.api_key:
            logger.error("OPENET_API_KEY not set")
            return {
                "status": DataLoadStatus.ERROR,
                "data": None,
                "provenance": DataProvenance.API,
                "error_type": DataErrorType.PERMISSION,
                "error": "OPENET_API_KEY not set",
                **base_metadata,
            }

        key = f"openet:{lon}:{lat}:{start_date}:{end_date}:{source}"

        # Check cache first
        if use_cache:
            cached = _CACHE.get(key)
            if cached is not None:
                logger.info(f"OpenET cache hit for ({lon}, {lat})")
                return {
                    "status": DataLoadStatus.SUCCESS,
                    "data": cached,
                    "provenance": DataProvenance.STATIC,
                    "error_type": None,
                    "error": None,
                    **base_metadata,
                }

        geometry = f"POINT({lon} {lat})"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "geometry": geometry,
            "source": source,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            logger.info(f"OpenET API request for ({lon}, {lat})")
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            result_data = response.json()

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
            logger.error(f"OpenET API request failed: {e}")
            return {
                "status": DataLoadStatus.ERROR,
                "data": None,
                "provenance": DataProvenance.API,
                "error_type": DataErrorType.NETWORK,
                "error": f"OpenET API request failed: {e}",
                **base_metadata,
            }
        except Exception as e:
            logger.error(f"Unexpected error in OpenET query: {e}")
            return {
                "status": DataLoadStatus.ERROR,
                "data": None,
                "provenance": DataProvenance.API,
                "error_type": DataErrorType.UNKNOWN,
                "error": f"Unexpected error: {e}",
                **base_metadata,
            }

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata about this data source."""
        return {
            "name": "OpenET API",
            "description": "Evapotranspiration data for water management",
            "api_documentation": "https://etdata.org/api-info/",
            "requires_api_key": True,
            "api_key_env_var": "OPENET_API_KEY",
            "domain": DataDomain.WATER.value,
            "update_frequency": DataUpdateFrequency.DAILY.value,
            "access_level": DataAccessLevel.RESTRICTED.value,
        }


# Convenience function for ADK tool registration
def get_openet_et(
    lon: float,
    lat: float,
    start_date: str,
    end_date: str,
    source: str = "ensemble",
) -> dict[str, Any]:
    """
    Get OpenET evapotranspiration data (ADK tool wrapper).

    Args:
        lon: Longitude
        lat: Latitude
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        source: Data source (default: 'ensemble')

    Returns:
        dict: Standardized result with ET data
    """
    datasource = OpenETDataSource()
    return datasource.get_et(lon, lat, start_date, end_date, source)
