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
    "wildfire": {
        "high": {
            "criteria": "Red Flag Warning issued or Fire Weather Watch with relative humidity < 20% and winds > 30 mph",
            "source": "FEMA Wildfire Risk to Communities",
            "url": "https://wildfirerisk.org/"
        },
        "medium": {
            "criteria": "Elevated fire weather conditions with relative humidity < 30% and winds > 20 mph",
            "source": "FEMA Wildfire Risk to Communities",
            "url": "https://wildfirerisk.org/"
        }
    },
    "extreme_storms": {
        "high": {
            "criteria": "Severe Thunderstorm Warning issued or wind speeds > 58 mph",
            "source": "National Weather Service",
            "url": "https://www.weather.gov/safety/thunderstorm"
        },
        "medium": {
            "criteria": "Severe Thunderstorm Watch issued or wind speeds > 40 mph",
            "source": "National Weather Service",
            "url": "https://www.weather.gov/safety/thunderstorm"
        }
    },
    "extreme_heat": {
        "high": {
            "criteria": "Excessive Heat Warning issued or heat index > 105°F (40.6°C)",
            "source": "National Weather Service",
            "url": "https://www.weather.gov/safety/heat"
        },
        "medium": {
            "criteria": "Heat Advisory issued or heat index > 100°F (37.8°C)",
            "source": "National Weather Service",
            "url": "https://www.weather.gov/safety/heat"
        }
    }
}

# Insurance Industry Definitions (ISO - Insurance Services Office)
ISO_DEFINITIONS = {
    "flooding": {
        "high": {
            "criteria": "100-year floodplain or > 40mm rainfall in 1 hour",
            "source": "ISO Property Evaluation Schedule",
            "url": "https://www.iso.com/"
        },
        "medium": {
            "criteria": "500-year floodplain or > 25mm rainfall in 1 hour",
            "source": "ISO Property Evaluation Schedule",
            "url": "https://www.iso.com/"
        }
    },
    "wildfire": {
        "high": {
            "criteria": "ISO Wildfire Risk Score > 80 or relative humidity < 25% with winds > 25 mph",
            "source": "ISO Wildfire Risk Assessment",
            "url": "https://www.iso.com/"
        },
        "medium": {
            "criteria": "ISO Wildfire Risk Score > 60 or relative humidity < 35% with winds > 20 mph",
            "source": "ISO Wildfire Risk Assessment",
            "url": "https://www.iso.com/"
        }
    },
    "extreme_storms": {
        "high": {
            "criteria": "Hail > 1 inch or wind speeds > 50 mph",
            "source": "ISO Catastrophe Risk Evaluation",
            "url": "https://www.iso.com/"
        },
        "medium": {
            "criteria": "Hail > 0.75 inch or wind speeds > 40 mph",
            "source": "ISO Catastrophe Risk Evaluation",
            "url": "https://www.iso.com/"
        }
    },
    "extreme_heat": {
        "high": {
            "criteria": "Temperature > 100°F (37.8°C) for 3+ consecutive days",
            "source": "ISO Catastrophe Risk Evaluation",
            "url": "https://www.iso.com/"
        },
        "medium": {
            "criteria": "Temperature > 95°F (35°C) for 3+ consecutive days",
            "source": "ISO Catastrophe Risk Evaluation",
            "url": "https://www.iso.com/"
        }
    }
}

# World Health Organization (WHO) Definitions
WHO_DEFINITIONS = {
    "extreme_heat": {
        "high": {
            "criteria": "Temperature > 40°C or heat index > 54°C",
            "source": "WHO Heat Health Action Plans",
            "url": "https://www.who.int/health-topics/heatwaves"
        },
        "medium": {
            "criteria": "Temperature > 35°C or heat index > 41°C",
            "source": "WHO Heat Health Action Plans",
            "url": "https://www.who.int/health-topics/heatwaves"
        }
    }
}

# National Oceanic and Atmospheric Administration (NOAA) Definitions
NOAA_DEFINITIONS = {
    "extreme_storms": {
        "high": {
            "criteria": "Severe Thunderstorm Warning or wind speeds > 58 mph",
            "source": "NOAA Storm Prediction Center",
            "url": "https://www.spc.noaa.gov/"
        },
        "medium": {
            "criteria": "Severe Thunderstorm Watch or wind speeds > 40 mph",
            "source": "NOAA Storm Prediction Center",
            "url": "https://www.spc.noaa.gov/"
        }
    }
}

# Validate all definitions
for source_name, definitions in [
    ("FEMA", FEMA_DEFINITIONS),
    ("ISO", ISO_DEFINITIONS),
    ("WHO", WHO_DEFINITIONS),
    ("NOAA", NOAA_DEFINITIONS)
]:
    for risk_type, risk_def in definitions.items():
        validate_risk_definition(risk_def)

# Consensus thresholds combining multiple sources
def get_consensus_thresholds() -> Dict:
    """Get consensus thresholds for different risk types.
    
    Returns:
        Dict: Consensus thresholds for flooding, wildfire, extreme storms, and extreme heat.
    """
    return {
        "flooding": {
            "high": {
                "rainfall_1h": 50.0,  # mm
                "sources": ["FEMA", "ISO"]
            },
            "medium": {
                "rainfall_1h": 20.0,  # mm
                "sources": ["FEMA", "ISO"]
            }
        },
        "wildfire": {
            "high": {
                "temperature": 35.0,  # °C
                "humidity": 20.0,     # %
                "wind_speed": 13.4,   # m/s (30 mph)
                "sources": ["FEMA", "ISO"]
            },
            "medium": {
                "temperature": 30.0,  # °C
                "humidity": 30.0,     # %
                "wind_speed": 8.9,    # m/s (20 mph)
                "sources": ["FEMA", "ISO"]
            }
        },
        "extreme_storms": {
            "high": {
                "wind_speed": 25.7,   # m/s (58 mph)
                "sources": ["FEMA", "NOAA"]
            },
            "medium": {
                "wind_speed": 17.9,   # m/s (40 mph)
                "sources": ["FEMA", "NOAA"]
            }
        },
        "extreme_heat": {
            "high": {
                "temperature": 40.6,  # °C (105°F)
                "sources": ["FEMA", "WHO"]
            },
            "medium": {
                "temperature": 37.8,  # °C (100°F)
                "sources": ["FEMA", "WHO"]
            }
        }
    }

# Severity levels used in risk analysis
severity_levels = ["high", "medium"] 