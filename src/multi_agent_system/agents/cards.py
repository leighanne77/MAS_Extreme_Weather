from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentCard:
    name: str
    description: str
    url: str
    version: str
    capabilities: Dict[str, bool]
    skills: List[Dict[str, Any]]
    security_schemes: Optional[Dict[str, Any]] = None
    default_input_modes: List[str] = None
    default_output_modes: List[str] = None
    metadata: Dict[str, Any] = None

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