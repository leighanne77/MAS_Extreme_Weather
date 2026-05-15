#!/usr/bin/env python3
"""
Simple test script to verify json data files work correctly.
"""
import json
import logging
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestJsonDataFiles:
    """Test that all JSON data files load correctly."""
    
    @pytest.fixture
    def data_dir(self):
        """Get the data directory path."""
        return Path(__file__).parent.parent / "src" / "multi_agent_system" / "data"
    
    def test_nature_based_solutions_json(self, data_dir):
        """Test nature_based_solutions.json loads correctly."""
        json_file = data_dir / "nature_based_solutions.json"
        assert json_file.exists(), f"File not found: {json_file}"
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert "solutions" in data
        assert len(data["solutions"]) > 0
        logger.info("Loaded %d nature-based solutions", len(data["solutions"]))
    
    def test_historical_weather_events_json(self, data_dir):
        """Test historical_weather_events.json loads correctly."""
        json_file = data_dir / "historical_weather_events.json"
        assert json_file.exists(), f"File not found: {json_file}"
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert "events" in data
        assert len(data["events"]) > 0
        logger.info("Loaded %d historical weather events", len(data["events"]))
    
    def test_economic_impact_data_json(self, data_dir):
        """Test economic_impact_data.json loads correctly."""
        json_file = data_dir / "economic_impact_data.json"
        assert json_file.exists(), f"File not found: {json_file}"
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert "economic_impacts" in data
        logger.info("Loaded economic impact data")
    
    def test_regional_risk_profiles_json(self, data_dir):
        """Test regional_risk_profiles.json loads correctly."""
        json_file = data_dir / "regional_risk_profiles.json"
        assert json_file.exists(), f"File not found: {json_file}"
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert "regions" in data
        assert len(data["regions"]) > 0
        logger.info("Loaded %d regional risk profiles", len(data["regions"]))
    
    def test_funding_sources_json(self, data_dir):
        """Test funding_sources_NSB.json loads correctly."""
        json_file = data_dir / "funding_sources_NSB.json"
        assert json_file.exists(), f"File not found: {json_file}"
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert data is not None
        logger.info("Loaded funding sources data")
    
    def test_opportunity_zones_json(self, data_dir):
        """Test opportunity_zones.json loads correctly."""
        json_file = data_dir / "opportunity_zones.json"
        assert json_file.exists(), f"File not found: {json_file}"
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert "opportunity_zones" in data or "metadata" in data
        logger.info("Loaded opportunity zones data")
    
    def test_all_json_files_valid(self, data_dir):
        """Test that all JSON files in data directory are valid JSON."""
        json_files = list(data_dir.glob("*.json"))
        assert len(json_files) > 0, "No JSON files found in data directory"
        
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
            assert data is not None, f"Failed to load {json_file.name}"
        
        logger.info("Validated %d JSON files", len(json_files))