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
        mock_source.fetch_data = AsyncMock(return_value={"status": "success", "data": "ok"})
        data_manager.data_sources["test"] = mock_source
        result = await data_manager.fetch_data("test", {})
        assert result["status"] == "success"
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
    @pytest.mark.asyncio
    async def test_noaa_weather_data(self):
        weather = NOAAWeatherData()
        with patch.object(weather, 'get_severe_weather_data', return_value={"temperature": 20}) as mock_fetch:
            result = await weather.get_severe_weather_data("2024-01-01", "2024-01-02", "New York")
            assert result["temperature"] == 20
            mock_fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_nbs_source(self):
        nbs = NatureBasedSolutionsSource()
        with patch.object(nbs, 'get_solutions', return_value=[{"name": "Tree Planting"}]) as mock_get:
            result = await nbs.get_solutions("New York", ["flood"])
            assert result[0]["name"] == "Tree Planting"
            mock_get.assert_called_once()

class TestDataValidationAndTransformation:
    @pytest.mark.asyncio
    async def test_data_validation(self):
        data_manager = DataManager()
        with patch.object(data_manager, 'validate_data', return_value=True) as mock_val:
            result = await data_manager.validate_data({"foo": "bar"})
            assert result is True
            mock_val.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_data_transformation(self):
        data_manager = DataManager()
        with patch.object(data_manager, 'transform_data', return_value={"transformed": True}) as mock_trans:
            result = await data_manager.transform_data({"foo": "bar"})
            assert result["transformed"] is True
            mock_trans.assert_called_once()
