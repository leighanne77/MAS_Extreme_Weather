"""
Tests for DataSourceManager - Unified Data Source Registry

Tests cover:
- Registration/unregistration
- Lookup by name and type
- JSON data loading
- Caching behavior
- Health checks
- Metrics collection
- Backward compatibility with DataLoader
"""

import pytest
from pathlib import Path
from datetime import datetime

from multi_agent_system.data.data_source_manager import (
    DataSourceManager,
    get_data_source_manager,
    DataSourceNotFoundError,
    DataSourceUnavailableError,
    DataSourceInfo,
)
from multi_agent_system.data.data_enums import DataSourceType


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def fresh_manager():
    """Get a fresh DataSourceManager instance (reset singleton)."""
    DataSourceManager.reset_instance()
    manager = get_data_source_manager()
    yield manager
    DataSourceManager.reset_instance()


@pytest.fixture
def manager():
    """Get the singleton DataSourceManager instance."""
    return get_data_source_manager()


# =============================================================================
# REGISTRATION TESTS
# =============================================================================

@pytest.mark.unit
class TestRegistration:
    """Tests for source registration and unregistration."""
    
    def test_register_source(self, fresh_manager):
        """Test registering a new source."""
        fresh_manager.register_source(
            name="test_source",
            source="/path/to/data.json",
            source_type=DataSourceType.JSON,
            description="Test source"
        )
        
        info = fresh_manager.get_source("test_source")
        assert info is not None
        assert info.name == "test_source"
        assert info.source_type == DataSourceType.JSON
        assert info.description == "Test source"
    
    def test_register_overwrites_existing(self, fresh_manager):
        """Test that registering with same name overwrites."""
        fresh_manager.register_source(
            name="test_source",
            source="/path/v1.json",
            source_type=DataSourceType.JSON,
            description="Version 1"
        )
        
        fresh_manager.register_source(
            name="test_source",
            source="/path/v2.json",
            source_type=DataSourceType.JSON,
            description="Version 2"
        )
        
        info = fresh_manager.get_source("test_source")
        assert info.description == "Version 2"
    
    def test_unregister_source(self, fresh_manager):
        """Test unregistering a source."""
        fresh_manager.register_source(
            name="temp_source",
            source="/path/to/temp.json",
            source_type=DataSourceType.JSON
        )
        
        assert fresh_manager.get_source("temp_source") is not None
        
        result = fresh_manager.unregister_source("temp_source")
        assert result is True
        assert fresh_manager.get_source("temp_source") is None
    
    def test_unregister_nonexistent(self, fresh_manager):
        """Test unregistering a source that doesn't exist."""
        result = fresh_manager.unregister_source("nonexistent")
        assert result is False


# =============================================================================
# LOOKUP TESTS
# =============================================================================

@pytest.mark.unit
class TestLookup:
    """Tests for source lookup methods."""
    
    def test_get_source_exists(self, manager):
        """Test getting an existing source."""
        info = manager.get_source("nature_based_solutions")
        assert info is not None
        assert info.name == "nature_based_solutions"
        assert info.source_type == DataSourceType.JSON
    
    def test_get_source_not_found(self, manager):
        """Test getting a non-existent source returns None."""
        info = manager.get_source("nonexistent_source")
        assert info is None
    
    def test_get_source_required_raises(self, manager):
        """Test getting a required non-existent source raises error."""
        with pytest.raises(DataSourceNotFoundError) as exc_info:
            manager.get_source("nonexistent_source", required=True)
        
        assert "nonexistent_source" in str(exc_info.value)
        assert exc_info.value.source_name == "nonexistent_source"
    
    def test_get_sources_by_type(self, manager):
        """Test filtering sources by type."""
        json_sources = manager.get_sources_by_type(DataSourceType.JSON)
        
        assert len(json_sources) > 0
        for source in json_sources:
            assert source.source_type == DataSourceType.JSON
    
    def test_list_sources(self, manager):
        """Test listing all sources."""
        sources = manager.list_sources()
        
        assert len(sources) > 0
        assert all(isinstance(s, DataSourceInfo) for s in sources)
    
    def test_get_source_names(self, manager):
        """Test getting list of source names."""
        names = manager.get_source_names()
        
        assert isinstance(names, list)
        assert "nature_based_solutions" in names


# =============================================================================
# DATA ACCESS TESTS
# =============================================================================

@pytest.mark.unit
class TestDataAccess:
    """Tests for data access methods."""
    
    def test_get_json_data(self, manager):
        """Test loading JSON data."""
        data = manager.get_json_data("nature_based_solutions")
        
        assert isinstance(data, dict)
        assert "solutions" in data
        assert len(data["solutions"]) > 0
    
    def test_get_json_data_not_found(self, manager):
        """Test loading non-existent JSON source raises error."""
        with pytest.raises(DataSourceNotFoundError):
            manager.get_json_data("nonexistent")
    
    def test_caching(self, manager):
        """Test that data is cached."""
        # First load
        data1 = manager.get_json_data("nature_based_solutions")
        
        # Second load should come from cache
        data2 = manager.get_json_data("nature_based_solutions")
        
        assert data1 is data2  # Same object from cache
    
    def test_clear_cache_specific(self, manager):
        """Test clearing cache for specific source."""
        # Load data to populate cache
        manager.get_json_data("nature_based_solutions")
        assert "nature_based_solutions" in manager._cache
        
        # Clear specific source
        manager.clear_cache("nature_based_solutions")
        assert "nature_based_solutions" not in manager._cache
    
    def test_clear_cache_all(self, manager):
        """Test clearing all cache."""
        # Load multiple sources
        manager.get_json_data("nature_based_solutions")
        manager.get_json_data("regional_risk_profiles")
        
        assert len(manager._cache) >= 2
        
        # Clear all
        manager.clear_cache()
        assert len(manager._cache) == 0


# =============================================================================
# BACKWARD COMPATIBILITY TESTS
# =============================================================================

@pytest.mark.unit
class TestBackwardCompatibility:
    """Tests for DataLoader backward compatibility."""
    
    def test_load_nature_based_solutions(self, manager):
        """Test DataLoader-compatible method."""
        data = manager.load_nature_based_solutions()
        
        assert isinstance(data, dict)
        assert "solutions" in data
    
    def test_load_historical_weather_events(self, manager):
        """Test DataLoader-compatible method."""
        data = manager.load_historical_weather_events()
        
        assert isinstance(data, dict)
        assert "events" in data
    
    def test_load_economic_impact_data(self, manager):
        """Test DataLoader-compatible method."""
        data = manager.load_economic_impact_data()
        
        assert isinstance(data, dict)
        assert "economic_impacts" in data
    
    def test_load_regional_risk_profiles(self, manager):
        """Test DataLoader-compatible method."""
        data = manager.load_regional_risk_profiles()
        
        assert isinstance(data, dict)
        assert "regions" in data
    
    def test_get_solution_by_id(self, manager):
        """Test getting solution by ID."""
        solution = manager.get_solution_by_id("wetland_restoration")
        
        assert solution is not None
        assert solution["id"] == "wetland_restoration"
    
    def test_get_solution_by_id_not_found(self, manager):
        """Test getting non-existent solution returns None."""
        solution = manager.get_solution_by_id("nonexistent_solution")
        assert solution is None
    
    def test_get_solutions_by_risk_type(self, manager):
        """Test filtering solutions by risk type."""
        solutions = manager.get_solutions_by_risk_type("flooding")
        
        assert len(solutions) > 0
        for s in solutions:
            assert "flooding" in s.get("risk_types", [])
    
    def test_get_regional_profile(self, manager):
        """Test getting regional profile."""
        profile = manager.get_regional_profile("gulf_coast")
        
        assert profile is not None
        assert "primary_risks" in profile
    
    def test_get_all_data_summary(self, manager):
        """Test getting data summary."""
        summary = manager.get_all_data_summary()
        
        assert "nature_based_solutions" in summary
        assert "historical_events" in summary
        assert "regions" in summary
        assert summary["nature_based_solutions"]["count"] > 0


# =============================================================================
# HEALTH & METRICS TESTS
# =============================================================================

@pytest.mark.unit
class TestHealthAndMetrics:
    """Tests for health checks and metrics."""
    
    def test_health_check_all(self, manager):
        """Test health check for all sources."""
        health = manager.health_check()
        
        assert isinstance(health, dict)
        assert len(health) > 0
        assert all(isinstance(v, bool) for v in health.values())
    
    def test_health_check_specific(self, manager):
        """Test health check for specific source."""
        health = manager.health_check("nature_based_solutions")
        
        assert "nature_based_solutions" in health
        assert health["nature_based_solutions"] is True
    
    def test_get_metrics(self, manager):
        """Test getting metrics."""
        metrics = manager.get_metrics()
        
        assert "total_sources" in metrics
        assert "available_sources" in metrics
        assert "sources" in metrics
        assert metrics["total_sources"] > 0
    
    def test_get_source_status(self, manager):
        """Test getting source status."""
        status = manager.get_source_status("nature_based_solutions")
        
        assert "name" in status
        assert "source_type" in status
        assert "is_available" in status
    
    def test_access_tracking(self, manager):
        """Test that access is tracked."""
        # Get initial count
        info = manager.get_source("nature_based_solutions")
        initial_count = info.access_count
        
        # Access again
        manager.get_source("nature_based_solutions")
        manager.get_source("nature_based_solutions")
        
        # Check count increased
        info = manager.get_source("nature_based_solutions")
        assert info.access_count > initial_count


# =============================================================================
# SINGLETON TESTS
# =============================================================================

@pytest.mark.unit
class TestSingleton:
    """Tests for singleton behavior."""
    
    def test_singleton_same_instance(self):
        """Test that get_data_source_manager returns same instance."""
        manager1 = get_data_source_manager()
        manager2 = get_data_source_manager()
        
        assert manager1 is manager2
    
    def test_singleton_direct_instantiation(self):
        """Test that direct instantiation also returns singleton."""
        manager1 = DataSourceManager()
        manager2 = DataSourceManager()
        
        assert manager1 is manager2
    
    def test_reset_instance(self, fresh_manager):
        """Test resetting singleton instance."""
        manager1 = get_data_source_manager()
        
        DataSourceManager.reset_instance()
        
        manager2 = get_data_source_manager()
        assert manager1 is not manager2


# =============================================================================
# IMPORT COMPATIBILITY TESTS
# =============================================================================

@pytest.mark.unit
class TestImportCompatibility:
    """Tests for import compatibility."""
    
    def test_import_from_data_module(self):
        """Test importing from data module."""
        from multi_agent_system.data import (
            DataSourceManager,
            get_data_source_manager,
            DataSourceNotFoundError,
        )
        
        assert DataSourceManager is not None
        assert callable(get_data_source_manager)
    
    def test_dataloader_alias(self):
        """Test that DataLoader is aliased to DataSourceManager."""
        from multi_agent_system.data import DataLoader
        
        # DataLoader should be same as DataSourceManager
        assert DataLoader is DataSourceManager
    
    def test_deprecated_get_data_loader(self):
        """Test that get_data_loader emits deprecation warning."""
        import warnings
        from multi_agent_system.data.data_source_manager import get_data_loader
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            loader = get_data_loader()
            
            # Check deprecation warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            
            # But it should still work
            assert isinstance(loader, DataSourceManager)


# =============================================================================
# API SOURCE TESTS
# =============================================================================

@pytest.mark.unit
class TestAPISourceRegistration:
    """Tests for API source registration and access."""
    
    def test_api_sources_registered(self, manager):
        """Test that API sources are auto-registered."""
        api_sources = manager.get_api_sources()
        
        # Should have some API sources registered
        assert len(api_sources) > 0
        
        # All should be API type
        for source in api_sources:
            assert source.source_type == DataSourceType.API
    
    def test_expected_api_sources_present(self, manager):
        """Test that expected API sources are registered."""
        expected_apis = ["bls_api", "census_api", "openfema_api", "eia_api", "usgs_water_api"]
        
        for api_name in expected_apis:
            source = manager.get_source(api_name)
            assert source is not None, f"Expected API source '{api_name}' not found"
            assert source.source_type == DataSourceType.API
    
    def test_api_source_has_metadata(self, manager):
        """Test that API sources have metadata."""
        bls = manager.get_source("bls_api")
        
        assert bls is not None
        assert "module" in bls.metadata
        assert "function" in bls.metadata
        assert "domain" in bls.metadata
    
    def test_api_source_callable(self, manager):
        """Test that API sources have callable functions."""
        bls = manager.get_source("bls_api")
        
        assert bls is not None
        assert callable(bls.source)
    
    def test_call_api_source_wrong_type_raises(self, manager):
        """Test that calling call_api_source on JSON source raises error."""
        with pytest.raises(ValueError, match="not an API source"):
            manager.call_api_source("nature_based_solutions")
    
    def test_call_api_source_not_found_raises(self, manager):
        """Test that calling non-existent API raises error."""
        with pytest.raises(DataSourceNotFoundError):
            manager.call_api_source("nonexistent_api")


@pytest.mark.unit
class TestExtendedJSONSources:
    """Tests for extended JSON source registration."""
    
    def test_alias_sources_work(self, manager):
        """Test that alias sources point to same data."""
        # weather_events should be alias for historical_weather_events
        weather = manager.get_source("weather_events")
        historical = manager.get_source("historical_weather_events")
        
        assert weather is not None
        assert historical is not None
        
        # Both should load same data
        weather_data = manager.get_json_data("weather_events")
        historical_data = manager.get_json_data("historical_weather_events")
        
        assert weather_data == historical_data
    
    def test_funding_sources_nsb_alias(self, manager):
        """Test funding_sources_NSB alias works."""
        source = manager.get_source("funding_sources_NSB")
        assert source is not None
        
        data = manager.get_json_data("funding_sources_NSB")
        assert data is not None
    
    def test_biodiversity_credits_available(self, manager):
        """Test biodiversity credits data is registered."""
        source = manager.get_source("biodiversity_credits")
        
        # May or may not exist depending on file presence
        if source is not None:
            assert source.source_type == DataSourceType.JSON
    
    def test_total_source_count(self, manager):
        """Test that we have the expected number of sources."""
        sources = manager.list_sources()
        
        # Should have at least 15 JSON + 5 API = 20 sources
        assert len(sources) >= 20
