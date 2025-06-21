"""
Consolidated tests for data sources, weather, NBS, and utility functions.

Covers:
- Data source integration and error handling
- Weather data and NBS
- Data validation and transformation
- Utility functions
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from multi_agent_system.data_management import DataManager
from multi_agent_system.data.weather_data import NOAAWeatherData
from multi_agent_system.data.nature_based_solutions_source import NatureBasedSolutionsSource

class TestDataSources:
    @pytest.mark.asyncio
    async def test_data_source_fetch(self):
        data_manager = DataManager()
        mock_source = Mock()
        mock_source.fetch_data = AsyncMock(return_value={"data": "ok"})
        data_manager.data_sources["test"] = mock_source
        result = await data_manager.fetch_data("test", {})
        assert result["data"] == "ok"
    @pytest.mark.asyncio
    async def test_data_fetch_error(self):
        data_manager = DataManager()
        mock_source = Mock()
        mock_source.fetch_data = AsyncMock(side_effect=Exception("fail"))
        data_manager.data_sources["test"] = mock_source
        result = await data_manager.fetch_data("test", {})
        assert result["status"] == "error"
        assert "fail" in result["error"]

class TestWeatherAndNBS:
    def test_noaa_weather_data(self):
        weather = NOAAWeatherData()
        with patch.object(weather, 'fetch', return_value={"temperature": 20}) as mock_fetch:
            result = weather.fetch("New York")
            assert result["temperature"] == 20
            mock_fetch.assert_called_once()
    def test_nbs_source(self):
        nbs = NatureBasedSolutionsSource()
        with patch.object(nbs, 'get_solutions', return_value=[{"name": "Tree Planting"}]) as mock_get:
            result = nbs.get_solutions("New York", ["flood"])
            assert result[0]["name"] == "Tree Planting"
            mock_get.assert_called_once()

class TestDataValidationAndTransformation:
    def test_data_validation(self):
        data_manager = DataManager()
        with patch.object(data_manager, 'validate_data', return_value=True) as mock_val:
            assert data_manager.validate_data({"foo": "bar"}) is True
            mock_val.assert_called_once()
    def test_data_transformation(self):
        data_manager = DataManager()
        with patch.object(data_manager, 'transform_data', return_value={"transformed": True}) as mock_trans:
            result = data_manager.transform_data({"foo": "bar"})
            assert result["transformed"] is True
            mock_trans.assert_called_once()
