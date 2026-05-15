"""
Data Loader Tools for ADK/A2A Integration

This module exposes data loader functions as ADK tools with:
- Standardized return values using enums from src/enums.py
- AgentCard-compatible metadata for discoverability
- Provenance and metrics tracking
- Batch processing and error handling

References:
    - Google Cloud Agent SDK: https://cloud.google.com/agent-sdk/docs
    - Google Cloud Agent Engine: https://cloud.google.com/agent-engine/docs
    - See docs/2-DATA/GEE A2A ADK.md for full implementation plan
"""
import logging
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable

from enums import (
    DataAccessLevel,
    DataDomain,
    DataErrorType,
    DataFormat,
    DataLoadStatus,
    DataProvenance,
    DataUpdateFrequency,
    ErrorSeverity,
)

logger = logging.getLogger(__name__)


@dataclass
class LoaderMetrics:
    """Metrics collected for each loader call."""
    call_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    last_call_time: float | None = None
    last_error: str | None = None
    
    def record_call(self, latency_ms: float, error: str | None = None) -> None:
        """Record a loader call."""
        self.call_count += 1
        self.total_latency_ms += latency_ms
        self.last_call_time = time.time()
        if error:
            self.error_count += 1
            self.last_error = error
    
    @property
    def avg_latency_ms(self) -> float:
        """Average latency in milliseconds."""
        if self.call_count == 0:
            return 0.0
        return self.total_latency_ms / self.call_count
    
    @property
    def error_rate(self) -> float:
        """Error rate as a fraction."""
        if self.call_count == 0:
            return 0.0
        return self.error_count / self.call_count
    
    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dict for inclusion in results."""
        return {
            "call_count": self.call_count,
            "error_count": self.error_count,
            "avg_latency_ms": self.avg_latency_ms,
            "error_rate": self.error_rate,
            "last_call_time": self.last_call_time,
        }


# Global metrics registry
_LOADER_METRICS: dict[str, LoaderMetrics] = {}


def get_loader_metrics(loader_name: str) -> LoaderMetrics:
    """Get or create metrics for a loader."""
    if loader_name not in _LOADER_METRICS:
        _LOADER_METRICS[loader_name] = LoaderMetrics()
    return _LOADER_METRICS[loader_name]


def adk_tool(
    name: str,
    description: str,
    domain: DataDomain,
    update_frequency: DataUpdateFrequency,
    access_level: DataAccessLevel = DataAccessLevel.PUBLIC,
    data_format: DataFormat = DataFormat.JSON,
):
    """
    Decorator to register a function as an ADK tool with metadata.
    
    This decorator:
    1. Wraps the function to add metrics collection
    2. Adds AgentCard-compatible metadata
    3. Ensures standardized return values
    
    Args:
        name: Tool name for AgentCard registration
        description: Tool description for discovery
        domain: Data domain (AGRICULTURE, WATER, etc.)
        update_frequency: How often data is updated
        access_level: Data access permissions
        data_format: Format of returned data
    
    Example:
        @adk_tool(
            name="get_farm_income",
            description="Get USDA ERS farm income data",
            domain=DataDomain.ECONOMIC,
            update_frequency=DataUpdateFrequency.ANNUAL,
        )
        def get_farm_income(year: int) -> dict[str, Any]:
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Store metadata on the function for AgentCard registration
        func._adk_tool_metadata = {
            "name": name,
            "description": description,
            "domain": domain,
            "update_frequency": update_frequency,
            "access_level": access_level,
            "data_format": data_format,
        }
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> dict[str, Any]:
            metrics = get_loader_metrics(name)
            start_time = time.time()
            error_msg = None
            
            try:
                result = func(*args, **kwargs)
                
                # Ensure result has metrics
                if isinstance(result, dict) and "metrics" not in result:
                    result["metrics"] = metrics.to_dict()
                
                return result
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"ADK tool {name} failed: {e}")
                return {
                    "status": DataLoadStatus.ERROR,
                    "data": None,
                    "provenance": DataProvenance.API,
                    "error_type": DataErrorType.UNKNOWN,
                    "error": error_msg,
                    "update_frequency": update_frequency,
                    "data_format": data_format,
                    "access_level": access_level,
                    "domain": domain,
                    "metrics": metrics.to_dict(),
                }
            finally:
                latency_ms = (time.time() - start_time) * 1000
                metrics.record_call(latency_ms, error_msg)
        
        return wrapper
    return decorator


@dataclass
class DataLoaderAgentCard:
    """
    AgentCard-compatible metadata for data loaders.
    
    This class provides a standardized way to register data loaders
    as discoverable tools in the ADK/A2A system.
    """
    name: str
    description: str
    version: str
    domain: DataDomain
    update_frequency: DataUpdateFrequency
    access_level: DataAccessLevel
    data_format: DataFormat
    capabilities: dict[str, bool] = field(default_factory=dict)
    skills: list[dict[str, Any]] = field(default_factory=list)
    
    def to_agent_card_dict(self) -> dict[str, Any]:
        """Convert to AgentCard-compatible dict format."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": {
                "data_loading": True,
                "caching": True,
                "error_handling": True,
                "metrics_collection": True,
                **self.capabilities,
            },
            "skills": self.skills,
            "metadata": {
                "domain": self.domain.value,
                "update_frequency": self.update_frequency.value,
                "access_level": self.access_level.value,
                "data_format": self.data_format.value,
            },
        }


# Registry of data loader AgentCards
DATA_LOADER_CARDS: dict[str, DataLoaderAgentCard] = {}


def register_data_loader_card(card: DataLoaderAgentCard) -> None:
    """Register a data loader AgentCard for discovery."""
    DATA_LOADER_CARDS[card.name] = card
    logger.info(f"Registered data loader AgentCard: {card.name}")


def get_all_data_loader_cards() -> list[dict[str, Any]]:
    """Get all registered data loader AgentCards as dicts."""
    return [card.to_agent_card_dict() for card in DATA_LOADER_CARDS.values()]


# Pre-register known data loader cards
ERS_LOADER_CARD = DataLoaderAgentCard(
    name="ers_data_loader",
    description="USDA Economic Research Service data loader for farm income and financial indicators",
    version="1.0.0",
    domain=DataDomain.ECONOMIC,
    update_frequency=DataUpdateFrequency.ANNUAL,
    access_level=DataAccessLevel.PUBLIC,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "ers_query",
            "description": "Query ERS API for economic data",
            "parameters": {
                "endpoint": {"type": "string", "required": True},
                "params": {"type": "object", "required": True},
                "use_cache": {"type": "boolean", "default": True},
            },
        },
        {
            "name": "get_farm_income",
            "description": "Get farm income data for a specific year",
            "parameters": {
                "year": {"type": "integer", "required": True},
            },
        },
    ],
)

NASS_LOADER_CARD = DataLoaderAgentCard(
    name="nass_data_loader",
    description="USDA NASS Quick Stats data loader for crop yields and production",
    version="1.0.0",
    domain=DataDomain.AGRICULTURE,
    update_frequency=DataUpdateFrequency.WEEKLY,
    access_level=DataAccessLevel.PUBLIC,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "nass_query",
            "description": "Query NASS Quick Stats API for crop data",
            "parameters": {
                "params": {"type": "object", "required": True, "description": "Must include 'key' for API key"},
                "use_cache": {"type": "boolean", "default": True},
            },
        },
        {
            "name": "get_crop_yield",
            "description": "Get crop yield data for a specific commodity, year, and optional state",
            "parameters": {
                "api_key": {"type": "string", "required": True},
                "commodity_desc": {"type": "string", "required": True},
                "year": {"type": "integer", "required": True},
                "state_alpha": {"type": "string", "required": False},
            },
        },
    ],
)

BLS_LOADER_CARD = DataLoaderAgentCard(
    name="bls_data_loader",
    description="Bureau of Labor Statistics data loader for employment and wage data",
    version="1.0.0",
    domain=DataDomain.ECONOMIC,
    update_frequency=DataUpdateFrequency.MONTHLY,
    access_level=DataAccessLevel.PUBLIC,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "get_bls_data",
            "description": "Query BLS API for labor statistics",
            "parameters": {
                "series_ids": {"type": "array", "required": True},
                "start_year": {"type": "string", "required": True},
                "end_year": {"type": "string", "required": True},
                "use_cache": {"type": "boolean", "default": True},
            },
        },
    ],
)

CENSUS_LOADER_CARD = DataLoaderAgentCard(
    name="census_data_loader",
    description="US Census Bureau data loader for demographic and economic data",
    version="1.0.0",
    domain=DataDomain.ECONOMIC,
    update_frequency=DataUpdateFrequency.ANNUAL,
    access_level=DataAccessLevel.PUBLIC,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "get_census_data",
            "description": "Query Census API for demographic data",
            "parameters": {
                "year": {"type": "string", "required": True},
                "dataset": {"type": "string", "required": True},
                "params": {"type": "object", "required": False},
                "use_cache": {"type": "boolean", "default": True},
            },
        },
    ],
)

OPENFEMA_LOADER_CARD = DataLoaderAgentCard(
    name="openfema_data_loader",
    description="FEMA disaster data loader for hazard declarations",
    version="1.0.0",
    domain=DataDomain.ENVIRONMENTAL,
    update_frequency=DataUpdateFrequency.DAILY,
    access_level=DataAccessLevel.PUBLIC,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "get_openfema_data",
            "description": "Query OpenFEMA API for disaster data",
            "parameters": {
                "dataset": {"type": "string", "required": True},
                "params": {"type": "object", "required": False},
                "use_cache": {"type": "boolean", "default": True},
            },
        },
    ],
)

EIA_LOADER_CARD = DataLoaderAgentCard(
    name="eia_data_loader",
    description="Energy Information Administration data loader for energy data",
    version="1.0.0",
    domain=DataDomain.ECONOMIC,
    update_frequency=DataUpdateFrequency.DAILY,
    access_level=DataAccessLevel.PUBLIC,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "get_eia_data",
            "description": "Query EIA API for energy data",
            "parameters": {
                "series_id": {"type": "string", "required": True},
                "use_cache": {"type": "boolean", "default": True},
            },
        },
    ],
)

FHFA_LOADER_CARD = DataLoaderAgentCard(
    name="fhfa_data_loader",
    description="Federal Housing Finance Agency data loader for house price index",
    version="1.0.0",
    domain=DataDomain.ECONOMIC,
    update_frequency=DataUpdateFrequency.QUARTERLY,
    access_level=DataAccessLevel.PUBLIC,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "get_fhfa_data",
            "description": "Query FHFA API for house price data",
            "parameters": {
                "params": {"type": "object", "required": False},
                "use_cache": {"type": "boolean", "default": True},
            },
        },
    ],
)

OPENET_LOADER_CARD = DataLoaderAgentCard(
    name="openet_data_loader",
    description="OpenET data loader for evapotranspiration data",
    version="1.0.0",
    domain=DataDomain.WATER,
    update_frequency=DataUpdateFrequency.DAILY,
    access_level=DataAccessLevel.RESTRICTED,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "get_openet_et",
            "description": "Get evapotranspiration data for a location",
            "parameters": {
                "lon": {"type": "number", "required": True},
                "lat": {"type": "number", "required": True},
                "start_date": {"type": "string", "required": True},
                "end_date": {"type": "string", "required": True},
                "source": {"type": "string", "default": "ensemble"},
            },
        },
    ],
)

USDA_NASS_LOADER_CARD = DataLoaderAgentCard(
    name="usda_nass_data_loader",
    description="USDA NASS Quick Stats data loader for crop statistics",
    version="1.0.0",
    domain=DataDomain.AGRICULTURE,
    update_frequency=DataUpdateFrequency.WEEKLY,
    access_level=DataAccessLevel.PUBLIC,
    data_format=DataFormat.JSON,
    skills=[
        {
            "name": "get_nass_data",
            "description": "Query USDA NASS Quick Stats API",
            "parameters": {
                "params": {"type": "object", "required": True},
                "use_cache": {"type": "boolean", "default": True},
            },
        },
    ],
)

# Register cards on module load
register_data_loader_card(ERS_LOADER_CARD)
register_data_loader_card(NASS_LOADER_CARD)
register_data_loader_card(BLS_LOADER_CARD)
register_data_loader_card(CENSUS_LOADER_CARD)
register_data_loader_card(OPENFEMA_LOADER_CARD)
register_data_loader_card(EIA_LOADER_CARD)
register_data_loader_card(FHFA_LOADER_CARD)
register_data_loader_card(OPENET_LOADER_CARD)
register_data_loader_card(USDA_NASS_LOADER_CARD)
