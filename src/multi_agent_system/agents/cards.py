from dataclasses import dataclass
from typing import Any

from enums import DataDomain, DataUpdateFrequency, DataAccessLevel, DataFormat


@dataclass
class AgentCard:
    name: str
    description: str
    url: str
    version: str
    capabilities: dict[str, bool]
    skills: list[dict[str, Any]]
    security_schemes: dict[str, Any] | None = None
    default_input_modes: list[str] = None
    default_output_modes: list[str] = None
    metadata: dict[str, Any] = None

# Define agent cards with ADK features
RISK_AGENT_CARDS = {
    "geocoding": AgentCard(
        name="Geocoding Agent",
        description="Validates and geocodes addresses for risk analysis",
        url="/api/geocoding",
        version="1.0.0",
        capabilities={
            "address_validation": True,
            "geocoding": True,
            "metadata_retrieval": True,
            "parallel_processing": True,
            "caching": True,
            "circuit_breaker": True
        },
        skills=[
            {
                "name": "validate_and_geocode",
                "description": "Validates and geocodes an address",
                "parameters": {
                    "address": {"type": "string", "required": True},
                    "validation_level": {"type": "string", "enum": ["basic", "strict"]},
                    "include_metadata": {"type": "boolean", "default": True}
                },
                "features": {
                    "caching": True,
                    "circuit_breaker": True,
                    "retry_logic": True
                }
            }
        ],
        metadata={
            "performance_metrics": True,
            "monitoring": True,
            "resource_management": True
        }
    ),
    "historical": AgentCard(
        name="Historical Analysis Agent",
        description="Analyzes historical weather and risk data",
        url="/api/historical",
        version="1.0.0",
        capabilities={
            "data_analysis": True,
            "trend_detection": True,
            "parallel_processing": True,
            "caching": True,
            "circuit_breaker": True
        },
        skills=[
            {
                "name": "analyze_historical_data",
                "description": "Analyzes historical weather and risk data",
                "parameters": {
                    "location": {"type": "object", "required": True},
                    "time_range": {"type": "object", "required": True},
                    "include_metadata": {"type": "boolean", "default": True}
                },
                "features": {
                    "caching": True,
                    "circuit_breaker": True,
                    "retry_logic": True
                }
            }
        ],
        metadata={
            "performance_metrics": True,
            "monitoring": True,
            "resource_management": True
        }
    ),
    "weather": AgentCard(
        name="Weather Agent",
        description="Analyzes current weather conditions",
        url="/api/weather",
        version="1.0.0",
        capabilities={
            "weather_analysis": True,
            "risk_assessment": True,
            "parallel_processing": True,
            "caching": True,
            "circuit_breaker": True
        },
        skills=[
            {
                "name": "get_current_conditions",
                "description": "Gets current weather conditions",
                "parameters": {
                    "location": {"type": "object", "required": True},
                    "include_metadata": {"type": "boolean", "default": True}
                },
                "features": {
                    "caching": True,
                    "circuit_breaker": True,
                    "retry_logic": True
                }
            }
        ],
        metadata={
            "performance_metrics": True,
            "monitoring": True,
            "resource_management": True
        }
    ),
    "risk": AgentCard(
        name="Risk Analysis Agent",
        description="Analyzes climate risks",
        url="/api/risk",
        version="1.0.0",
        capabilities={
            "risk_analysis": True,
            "impact_assessment": True,
            "parallel_processing": True,
            "caching": True,
            "circuit_breaker": True
        },
        skills=[
            {
                "name": "analyze_risks",
                "description": "Analyzes climate risks",
                "parameters": {
                    "location": {"type": "object", "required": True},
                    "historical_data": {"type": "object", "required": True},
                    "current_conditions": {"type": "object", "required": True},
                    "include_metadata": {"type": "boolean", "default": True}
                },
                "features": {
                    "caching": True,
                    "circuit_breaker": True,
                    "retry_logic": True
                }
            }
        ],
        metadata={
            "performance_metrics": True,
            "monitoring": True,
            "resource_management": True
        }
    ),
    "investment": AgentCard(
        name="Investment Impact Agent",
        description="Analyzes investment impact of climate risks",
        url="/api/investment",
        version="1.0.0",
        capabilities={
            "impact_analysis": True,
            "recommendation_generation": True,
            "parallel_processing": True,
            "caching": True,
            "circuit_breaker": True
        },
        skills=[
            {
                "name": "analyze_investment_impact",
                "description": "Analyzes investment impact of climate risks",
                "parameters": {
                    "risk_assessment": {"type": "object", "required": True},
                    "property_details": {"type": "object", "required": True},
                    "include_metadata": {"type": "boolean", "default": True}
                },
                "features": {
                    "caching": True,
                    "circuit_breaker": True,
                    "retry_logic": True
                }
            }
        ],
        metadata={
            "performance_metrics": True,
            "monitoring": True,
            "resource_management": True
        }
    ),
    "report": AgentCard(
        name="Report Generation Agent",
        description="Generates comprehensive risk analysis reports",
        url="/api/report",
        version="1.0.0",
        capabilities={
            "report_generation": True,
            "data_visualization": True,
            "parallel_processing": True,
            "caching": True,
            "circuit_breaker": True
        },
        skills=[
            {
                "name": "generate_report",
                "description": "Generates comprehensive risk analysis report",
                "parameters": {
                    "analysis_results": {"type": "object", "required": True},
                    "format": {"type": "string", "enum": ["json", "pdf", "html"]},
                    "include_metadata": {"type": "boolean", "default": True}
                },
                "features": {
                    "caching": True,
                    "circuit_breaker": True,
                    "retry_logic": True
                }
            }
        ],
        metadata={
            "performance_metrics": True,
            "monitoring": True,
            "resource_management": True
        }
    )
}

# Data Loader Agent Cards - imported from loader_tools for discoverability
# These expose data loading capabilities to the ADK/A2A system
DATA_LOADER_AGENT_CARDS = {
    "ers_data_loader": AgentCard(
        name="ERS Data Loader Agent",
        description="USDA Economic Research Service data loader for farm income and financial indicators",
        url="/api/data/ers",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
        skills=[
            {
                "name": "ers_query",
                "description": "Query ERS API for economic data",
                "parameters": {
                    "endpoint": {"type": "string", "required": True},
                    "params": {"type": "object", "required": True},
                    "use_cache": {"type": "boolean", "default": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
                },
            },
            {
                "name": "get_farm_income",
                "description": "Get farm income data for a specific year",
                "parameters": {
                    "year": {"type": "integer", "required": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.ECONOMIC.value,
            "update_frequency": DataUpdateFrequency.ANNUAL.value,
            "access_level": DataAccessLevel.PUBLIC.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
    "nass_data_loader": AgentCard(
        name="NASS Data Loader Agent",
        description="USDA NASS Quick Stats data loader for crop yields and production",
        url="/api/data/nass",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
        skills=[
            {
                "name": "nass_query",
                "description": "Query NASS Quick Stats API for crop data",
                "parameters": {
                    "params": {"type": "object", "required": True, "description": "Must include 'key' for API key"},
                    "use_cache": {"type": "boolean", "default": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
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
                "features": {
                    "caching": True,
                    "error_handling": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.AGRICULTURE.value,
            "update_frequency": DataUpdateFrequency.WEEKLY.value,
            "access_level": DataAccessLevel.PUBLIC.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
    # BLS Data Loader
    "bls_data_loader": AgentCard(
        name="BLS Data Loader Agent",
        description="Bureau of Labor Statistics data loader for employment and wage data",
        url="/api/data/bls",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
        skills=[
            {
                "name": "get_bls_data",
                "description": "Query BLS API for employment and labor statistics",
                "parameters": {
                    "series_ids": {"type": "array", "required": True, "items": {"type": "string"}},
                    "start_year": {"type": "string", "required": True},
                    "end_year": {"type": "string", "required": True},
                    "use_cache": {"type": "boolean", "default": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
                },
            },
            {
                "name": "get_unemployment_data",
                "description": "Get local area unemployment statistics",
                "parameters": {
                    "state_fips": {"type": "string", "required": True},
                    "county_fips": {"type": "string", "required": True},
                    "start_year": {"type": "string", "required": True},
                    "end_year": {"type": "string", "required": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.ECONOMIC.value,
            "update_frequency": DataUpdateFrequency.MONTHLY.value,
            "access_level": DataAccessLevel.PUBLIC.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
    # Census Data Loader
    "census_data_loader": AgentCard(
        name="Census Data Loader Agent",
        description="US Census Bureau data loader for demographic and economic data",
        url="/api/data/census",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
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
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
                },
            },
            {
                "name": "get_acs_population",
                "description": "Get American Community Survey population data",
                "parameters": {
                    "year": {"type": "string", "required": True},
                    "state_fips": {"type": "string", "required": True},
                    "county_fips": {"type": "string", "required": False},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.ECONOMIC.value,
            "update_frequency": DataUpdateFrequency.ANNUAL.value,
            "access_level": DataAccessLevel.PUBLIC.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
    # OpenFEMA Data Loader
    "openfema_data_loader": AgentCard(
        name="OpenFEMA Data Loader Agent",
        description="FEMA disaster data loader for hazard declarations and mitigation projects",
        url="/api/data/openfema",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
        skills=[
            {
                "name": "get_openfema_data",
                "description": "Query OpenFEMA API for disaster data",
                "parameters": {
                    "dataset": {"type": "string", "required": True},
                    "params": {"type": "object", "required": False},
                    "use_cache": {"type": "boolean", "default": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
                },
            },
            {
                "name": "get_disaster_declarations",
                "description": "Get FEMA disaster declarations",
                "parameters": {
                    "state": {"type": "string", "required": False},
                    "year": {"type": "integer", "required": False},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.ENVIRONMENTAL.value,
            "update_frequency": DataUpdateFrequency.DAILY.value,
            "access_level": DataAccessLevel.PUBLIC.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
    # EIA Data Loader
    "eia_data_loader": AgentCard(
        name="EIA Data Loader Agent",
        description="Energy Information Administration data loader for energy production and pricing",
        url="/api/data/eia",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
        skills=[
            {
                "name": "get_eia_data",
                "description": "Query EIA API for energy data",
                "parameters": {
                    "series_id": {"type": "string", "required": True},
                    "use_cache": {"type": "boolean", "default": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
                },
            },
            {
                "name": "get_electricity_price",
                "description": "Get average retail electricity price for a state",
                "parameters": {
                    "state": {"type": "string", "required": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.ECONOMIC.value,
            "update_frequency": DataUpdateFrequency.DAILY.value,
            "access_level": DataAccessLevel.PUBLIC.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
    # FHFA Data Loader
    "fhfa_data_loader": AgentCard(
        name="FHFA Data Loader Agent",
        description="Federal Housing Finance Agency data loader for house price index",
        url="/api/data/fhfa",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
        skills=[
            {
                "name": "get_fhfa_data",
                "description": "Query FHFA API for house price data",
                "parameters": {
                    "params": {"type": "object", "required": False},
                    "use_cache": {"type": "boolean", "default": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
                },
            },
            {
                "name": "get_state_hpi",
                "description": "Get House Price Index for a state",
                "parameters": {
                    "state": {"type": "string", "required": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.ECONOMIC.value,
            "update_frequency": DataUpdateFrequency.QUARTERLY.value,
            "access_level": DataAccessLevel.PUBLIC.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
    # OpenET Data Loader
    "openet_data_loader": AgentCard(
        name="OpenET Data Loader Agent",
        description="OpenET data loader for evapotranspiration and water use data",
        url="/api/data/openet",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
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
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.WATER.value,
            "update_frequency": DataUpdateFrequency.DAILY.value,
            "access_level": DataAccessLevel.RESTRICTED.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
    # USDA NASS Quick Stats Data Loader
    "usda_nass_data_loader": AgentCard(
        name="USDA NASS Data Loader Agent",
        description="USDA NASS Quick Stats data loader for crop and agricultural statistics",
        url="/api/data/usda_nass",
        version="1.0.0",
        capabilities={
            "data_loading": True,
            "caching": True,
            "error_handling": True,
            "metrics_collection": True,
        },
        skills=[
            {
                "name": "get_nass_data",
                "description": "Query USDA NASS Quick Stats API",
                "parameters": {
                    "params": {"type": "object", "required": True},
                    "use_cache": {"type": "boolean", "default": True},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                    "metrics_collection": True,
                },
            },
            {
                "name": "get_crop_production",
                "description": "Get crop production data",
                "parameters": {
                    "commodity": {"type": "string", "required": True},
                    "year": {"type": "integer", "required": True},
                    "state": {"type": "string", "required": False},
                },
                "features": {
                    "caching": True,
                    "error_handling": True,
                },
            },
        ],
        metadata={
            "domain": DataDomain.AGRICULTURE.value,
            "update_frequency": DataUpdateFrequency.WEEKLY.value,
            "access_level": DataAccessLevel.PUBLIC.value,
            "data_format": DataFormat.JSON.value,
            "performance_metrics": True,
            "provenance_tracking": True,
        },
    ),
}

# Combined agent cards for full system discovery
ALL_AGENT_CARDS = {**RISK_AGENT_CARDS, **DATA_LOADER_AGENT_CARDS}


def get_agent_card(agent_id: str) -> AgentCard | None:
    """Get an agent card by ID."""
    return ALL_AGENT_CARDS.get(agent_id)


def get_all_agent_cards() -> dict[str, AgentCard]:
    """Get all registered agent cards."""
    return ALL_AGENT_CARDS


def get_data_loader_cards() -> dict[str, AgentCard]:
    """Get all data loader agent cards."""
    return DATA_LOADER_AGENT_CARDS
