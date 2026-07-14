"""
Data handling and integration modules.

All data loaders use standardized enums from src/enums.py for:
- Status (DataLoadStatus)
- Provenance (DataProvenance)
- Domain (DataDomain)
- Error type (DataErrorType)
- Update frequency (DataUpdateFrequency)
- Data format (DataFormat)
- Access level (DataAccessLevel)

See docs/Definitions.md for full enum documentation.
"""

from enums import (
    ArtifactType,
    DataAccessLevel,
    DataDomain,
    DataErrorType,
    DataFormat,
    DataLoadStatus,
    DataProvenance,
    DataUpdateFrequency,
)

from .data_source import DataSource
from .nature_based_solutions_source import NatureBasedSolutionsSource
from .weather_data import NOAAWeatherData, get_weather_data
from .data_source_manager import (
    DataSourceManager,
    get_data_source_manager,
    DataSourceNotFoundError,
    DataSourceUnavailableError,
    DataSourceInfo,
)
from .erddap_mcp import ERDDAPDataProvider, get_erddap_provider
from .datagov_mcp import DataGovDataProvider, get_datagov_provider

__all__ = [
    # Primary interface
    'DataSourceManager',
    'get_data_source_manager',
    'DataSourceNotFoundError',
    'DataSourceUnavailableError',
    'DataSourceInfo',
    # Data sources
    'NOAAWeatherData',
    'get_weather_data',
    'DataSource',
    'NatureBasedSolutionsSource',
    # MCP providers
    'ERDDAPDataProvider',
    'get_erddap_provider',
    'DataGovDataProvider',
    'get_datagov_provider',
    # Enums (re-exported for convenience)
    'DataLoadStatus',
    'DataProvenance',
    'DataDomain',
    'DataErrorType',
    'DataUpdateFrequency',
    'DataFormat',
    'DataAccessLevel',
    'ArtifactType',
]
