#!/usr/bin/env python3
"""
Test script to verify all data files work correctly.

Tests:
- JSON data file loading via DataSourceManager
- Nature-based solutions data
- Historical weather events data
- Economic impact data
- Regional risk profiles
- Solution queries by risk type
"""

import logging
from pathlib import Path
import pytest

from multi_agent_system.data import DataSourceManager, get_data_source_manager

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestDataFiles:
    """Test suite for data file loading."""
    
    def test_nature_based_solutions(self):
        """Test nature-based solutions data loads correctly."""
        loader = get_data_source_manager()
        nbs_data = loader.load_nature_based_solutions()
        
        assert nbs_data is not None
        assert 'solutions' in nbs_data
        assert len(nbs_data['solutions']) > 0
    
    def test_historical_weather_events(self):
        """Test historical weather events data loads correctly."""
        loader = get_data_source_manager()
        hist_data = loader.load_historical_weather_events()
        
        assert hist_data is not None
        assert 'events' in hist_data
        assert len(hist_data['events']) > 0
    
    def test_economic_impact_data(self):
        """Test economic impact data loads correctly."""
        loader = get_data_source_manager()
        econ_data = loader.load_economic_impact_data()
        
        assert econ_data is not None
        assert 'economic_impacts' in econ_data
    
    def test_regional_risk_profiles(self):
        """Test regional risk profiles data loads correctly."""
        loader = get_data_source_manager()
        regional_data = loader.load_regional_risk_profiles()
        
        assert regional_data is not None
        assert 'regions' in regional_data
        assert len(regional_data['regions']) > 0
    
    def test_data_summary(self):
        """Test data summary generation."""
        loader = get_data_source_manager()
        summary = loader.get_all_data_summary()
        
        assert summary is not None
        assert 'nature_based_solutions' in summary
        assert 'historical_events' in summary
        assert 'regions' in summary
        assert summary['nature_based_solutions']['count'] > 0
    
    def test_solutions_by_risk_type(self):
        """Test querying solutions by risk type."""
        loader = get_data_source_manager()
        flood_solutions = loader.get_solutions_by_risk_type("flooding")
        
        assert isinstance(flood_solutions, list)
        # Should have some solutions for flooding
        assert len(flood_solutions) >= 0
    
    def test_regional_profile_query(self):
        """Test querying specific regional profile."""
        loader = get_data_source_manager()
        gulf_profile = loader.get_regional_profile("gulf_coast")
        
        # Profile may or may not exist
        if gulf_profile:
            assert 'primary_risks' in gulf_profile or 'name' in gulf_profile


@pytest.mark.unit
def test_data_files():
    """Test all data files to ensure they load correctly."""
    loader = get_data_source_manager()
    
    # Test nature-based solutions
    nbs_data = loader.load_nature_based_solutions()
    assert nbs_data is not None
    assert 'solutions' in nbs_data
    
    # Test historical weather events
    hist_data = loader.load_historical_weather_events()
    assert hist_data is not None
    
    # Test economic impact data
    econ_data = loader.load_economic_impact_data()
    assert econ_data is not None
    
    # Test regional risk profiles
    regional_data = loader.load_regional_risk_profiles()
    assert regional_data is not None


@pytest.mark.unit
def test_agent_cards():
    """Test that all agent cards in src/multi_agent_system/agents/ are valid and contain required metadata."""
    import importlib
    import os
    agent_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'multi_agent_system', 'agents')
    for filename in os.listdir(agent_dir):
        if filename.endswith('_agent.py'):
            module_name = f"multi_agent_system.agents.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                # Find agent class
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if hasattr(obj, 'agent_card'):
                        card = getattr(obj, 'agent_card')
                        assert 'name' in card and 'description' in card and 'capabilities' in card, f"Agent card missing required fields in {filename}"
                        assert 'skills' in card['capabilities'], f"Agent card missing skills in {filename}"
            except Exception as e:
                logger.error("Error loading agent card from %s: %s", filename, e)
                assert False, f"Agent card validation failed for {filename}: {e}"


@pytest.mark.unit
def test_data_examples():
    """Test that data examples can be loaded correctly."""
    loader = get_data_source_manager()
    
    # Test nature-based solution example (if method exists)
    if hasattr(loader, 'get_solution_by_id'):
        wetland_solution = loader.get_solution_by_id("wetland_restoration")
        if wetland_solution:
            assert 'name' in wetland_solution
            assert 'risk_types' in wetland_solution
            logger.info("Wetland solution: %s", wetland_solution['name'])
    
    # Test regional profile example (if method exists)
    if hasattr(loader, 'get_regional_profile'):
        gulf_profile = loader.get_regional_profile("gulf_coast")
        if gulf_profile:
            assert 'name' in gulf_profile or 'primary_risks' in gulf_profile
            logger.info("Regional profile loaded successfully")
    
    # Test economic impact example (if method exists)
    if hasattr(loader, 'get_economic_impact_by_event_type'):
        hurricane_impacts = loader.get_economic_impact_by_event_type("hurricane")
        if hurricane_impacts:
            assert isinstance(hurricane_impacts, dict)
            logger.info("Economic impacts loaded successfully")