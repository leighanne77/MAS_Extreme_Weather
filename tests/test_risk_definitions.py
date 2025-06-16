"""
Tests for risk definitions functionality.
"""

import pytest
from src.multi_agent_system.risk_definitions import (
    RiskType,
    RiskLevel,
    RiskThreshold,
    RiskDefinition,
    validate_risk_threshold,
    validate_risk_definition,
    get_risk_level,
    get_consensus_threshold
)

def test_risk_type_enum():
    """Test RiskType enum values."""
    assert RiskType.TEMPERATURE.value == "temperature"
    assert RiskType.PRECIPITATION.value == "precipitation"
    assert RiskType.WIND.value == "wind"
    assert RiskType.HUMIDITY.value == "humidity"
    assert RiskType.AIR_QUALITY.value == "air_quality"

def test_risk_level_enum():
    """Test RiskLevel enum values."""
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MODERATE.value == "moderate"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.EXTREME.value == "extreme"

def test_risk_threshold_validation():
    """Test risk threshold validation."""
    # Valid threshold
    threshold = RiskThreshold(
        min_value=0,
        max_value=100,
        unit="celsius",
        risk_level=RiskLevel.MODERATE
    )
    assert validate_risk_threshold(threshold) is True
    
    # Invalid threshold (min > max)
    invalid_threshold = RiskThreshold(
        min_value=100,
        max_value=0,
        unit="celsius",
        risk_level=RiskLevel.MODERATE
    )
    assert validate_risk_threshold(invalid_threshold) is False

def test_risk_definition_validation():
    """Test risk definition validation."""
    # Valid definition
    definition = RiskDefinition(
        risk_type=RiskType.TEMPERATURE,
        description="Temperature risk",
        thresholds=[
            RiskThreshold(0, 30, "celsius", RiskLevel.LOW),
            RiskThreshold(30, 40, "celsius", RiskLevel.MODERATE),
            RiskThreshold(40, 50, "celsius", RiskLevel.HIGH),
            RiskThreshold(50, float("inf"), "celsius", RiskLevel.EXTREME)
        ]
    )
    assert validate_risk_definition(definition) is True
    
    # Invalid definition (overlapping thresholds)
    invalid_definition = RiskDefinition(
        risk_type=RiskType.TEMPERATURE,
        description="Invalid temperature risk",
        thresholds=[
            RiskThreshold(0, 30, "celsius", RiskLevel.LOW),
            RiskThreshold(20, 40, "celsius", RiskLevel.MODERATE)  # Overlaps with LOW
        ]
    )
    assert validate_risk_definition(invalid_definition) is False

def test_get_risk_level():
    """Test getting risk level for a value."""
    definition = RiskDefinition(
        risk_type=RiskType.TEMPERATURE,
        description="Temperature risk",
        thresholds=[
            RiskThreshold(0, 30, "celsius", RiskLevel.LOW),
            RiskThreshold(30, 40, "celsius", RiskLevel.MODERATE),
            RiskThreshold(40, 50, "celsius", RiskLevel.HIGH),
            RiskThreshold(50, float("inf"), "celsius", RiskLevel.EXTREME)
        ]
    )
    
    assert get_risk_level(definition, 25) == RiskLevel.LOW
    assert get_risk_level(definition, 35) == RiskLevel.MODERATE
    assert get_risk_level(definition, 45) == RiskLevel.HIGH
    assert get_risk_level(definition, 55) == RiskLevel.EXTREME

def test_get_consensus_threshold():
    """Test getting consensus threshold."""
    # Test with multiple risk levels
    risk_levels = [
        RiskLevel.LOW,
        RiskLevel.LOW,
        RiskLevel.MODERATE,
        RiskLevel.HIGH
    ]
    assert get_consensus_threshold(risk_levels) == RiskLevel.MODERATE
    
    # Test with unanimous risk levels
    risk_levels = [RiskLevel.HIGH, RiskLevel.HIGH, RiskLevel.HIGH]
    assert get_consensus_threshold(risk_levels) == RiskLevel.HIGH
    
    # Test with empty list
    assert get_consensus_threshold([]) == RiskLevel.LOW 