

"""
Risk definitions from major governmental and insurance providers.
These definitions are used to standardize risk assessment across different sources.

This module provides standardized risk definitions and thresholds from authoritative sources:
- FEMA (Federal Emergency Management Agency)
- ISO (Insurance Services Office)
- WHO (World Health Organization)
- NOAA (National Oceanic and Atmospheric Administration)

Each risk type (flooding, wildfire, extreme storms, extreme heat) has:
- High and medium severity thresholds
- Source information and URLs
- Consensus thresholds combining multiple sources
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RiskSource:
    """Represents a source of risk definition with metadata."""
    criteria: str
    source: str
    url: str
    last_updated: datetime = datetime.now()

@dataclass
class RiskThreshold:
    """Represents a risk threshold with its parameters and metadata."""
    description: str
    sources: List[str]
    temperature: float = None
    humidity: float = None
    wind_speed: float = None
    rainfall_1h: float = None

def validate_risk_definition(definition: Dict) -> bool:
    """Validate a risk definition dictionary.
    
    Args:
        definition (Dict): Risk definition to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValueError: If definition is invalid
    """
    required_keys = {"high", "medium"}
    required_severity_keys = {"criteria", "source", "url"}
    
    if not all(key in definition for key in required_keys):
        raise ValueError(f"Risk definition must contain {required_keys}")
        
    for severity in definition.values():
        if not all(key in severity for key in required_severity_keys):
            raise ValueError(f"Severity level must contain {required_severity_keys}")
            
    return True

# FEMA (Federal Emergency Management Agency) Definitions
FEMA_DEFINITIONS = {
    "flooding": {
        "high": {
            "criteria": "Flash flood warning issued or > 50mm rainfall in 1 hour",
            "source": "FEMA Flood Hazard Mapping",
            "url": "https://www.fema.gov/flood-maps"
        },
        "medium": {
            "criteria": "Flood watch issued or > 20mm rainfall in 1 hour",
            "source": "FEMA Flood Hazard Mapping",
            "url": "https://www.fema.gov/flood-maps"
        }
    },
    # ... rest of FEMA definitions ...
}

# Validate all definitions
for source_name, definitions in [
    ("FEMA", FEMA_DEFINITIONS),
    ("ISO", ISO_DEFINITIONS),
    ("WHO", WHO_DEFINITIONS),
    ("NOAA", NOAA_DEFINITIONS)
]:
    for risk_type, definition in definitions.items():
        try:
            validate_risk_definition(definition)
        except ValueError as e:
            raise ValueError(f"Invalid {source_name} definition for {risk_type}: {str(e)}")

def get_consensus_thresholds() -> Dict:
    """Returns consensus thresholds based on major governmental and insurance providers.
    
    These thresholds represent a balanced approach considering multiple authoritative sources.
    Each threshold includes:
    - Numerical values for risk parameters
    - Description of the risk level
    - List of authoritative sources
    
    Returns:
        Dict: A dictionary of risk thresholds with the following structure:
            {
                "risk_type": {
                    "severity": {
                        "parameter": value,
                        "description": str,
                        "sources": List[str]
                    }
                }
            }
            
    Raises:
        ValueError: If thresholds are invalid or inconsistent
    """
    thresholds = {
        "flooding": {
            "high": {
                "rainfall_1h": 50,  # mm
                "description": "Extreme rainfall conditions (> 50mm in 1 hour)",
                "sources": ["FEMA", "ISO"]
            },
            "medium": {
                "rainfall_1h": 20,  # mm
                "description": "Heavy rainfall conditions (> 20mm in 1 hour)",
                "sources": ["FEMA", "ISO"]
            }
        },
        # ... rest of thresholds ...
    }
    
    # Validate thresholds
    for risk_type, severity_levels in thresholds.items():
        for severity, params in severity_levels.items():
            if not isinstance(params.get("sources"), list):
                raise ValueError(f"Sources must be a list for {risk_type} {severity}")
            if not params.get("description"):
                raise ValueError(f"Missing description for {risk_type} {severity}")
                
    return thresholds