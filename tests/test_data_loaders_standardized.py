#!/usr/bin/env python3
# filepath: /Users/midnighthome/Builds/004_MAS_Climate/tests/test_data_loaders_standardized.py
"""
Tests for standardized data loaders with ADK/A2A compatibility.

Tests cover:
- Standardized return value structure
- Enum usage (DataLoadStatus, DataProvenance, etc.)
- Error handling
- Cache behavior
- Metadata compliance
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import MagicMock, patch

from enums import (
    DataAccessLevel,
    DataDomain,
    DataErrorType,
    DataFormat,
    DataLoadStatus,
    DataProvenance,
    DataUpdateFrequency,
)


class TestBLSLoader:
    """Tests for BLS API loader."""

    def test_bls_tool_metadata_exists(self):
        """Test that BLS tool metadata is defined."""
        from multi_agent_system.data.bls_api import BLS_TOOL_METADATA
        
        assert BLS_TOOL_METADATA["name"] == "bls_query"
        assert BLS_TOOL_METADATA["domain"] == DataDomain.ECONOMIC
        assert BLS_TOOL_METADATA["update_frequency"] == DataUpdateFrequency.MONTHLY

    @patch('multi_agent_system.data.bls_api.requests.post')
    def test_get_bls_data_success(self, mock_post):
        """Test successful BLS API call."""
        from multi_agent_system.data.bls_api import get_bls_data
        
        mock_post.return_value.json.return_value = {"Results": {"series": []}}
        mock_post.return_value.raise_for_status = MagicMock()
        
        result = get_bls_data(["TEST_SERIES"], "2020", "2024", use_cache=False)
        
        assert result["status"] == DataLoadStatus.SUCCESS
        assert result["provenance"] == DataProvenance.API
        assert result["domain"] == DataDomain.ECONOMIC
        assert result["update_frequency"] == DataUpdateFrequency.MONTHLY
        assert result["error_type"] is None

    @patch('multi_agent_system.data.bls_api.requests.post')
    def test_get_bls_data_network_error(self, mock_post):
        """Test BLS API network error handling."""
        from multi_agent_system.data.bls_api import get_bls_data
        import requests
        
        mock_post.side_effect = requests.RequestException("Connection failed")
        
        result = get_bls_data(["TEST_SERIES"], "2020", "2024", use_cache=False)
        
        assert result["status"] == DataLoadStatus.ERROR
        assert result["error_type"] == DataErrorType.NETWORK
        assert "Connection failed" in result["error"]


class TestCensusLoader:
    """Tests for Census API loader."""

    def test_census_tool_metadata_exists(self):
        """Test that Census tool metadata is defined."""
        from multi_agent_system.data.census_api import CENSUS_TOOL_METADATA
        
        assert CENSUS_TOOL_METADATA["name"] == "census_query"
        assert CENSUS_TOOL_METADATA["domain"] == DataDomain.ECONOMIC
        assert CENSUS_TOOL_METADATA["update_frequency"] == DataUpdateFrequency.ANNUAL

    @patch('multi_agent_system.data.census_api.requests.get')
    def test_get_census_data_success(self, mock_get):
        """Test successful Census API call."""
        from multi_agent_system.data.census_api import get_census_data
        
        mock_get.return_value.json.return_value = [["B01001_001E", "NAME"], ["12345", "Test County"]]
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = get_census_data("2020", "acs/acs5", {"get": "B01001_001E"}, use_cache=False)
        
        assert result["status"] == DataLoadStatus.SUCCESS
        assert result["provenance"] == DataProvenance.API
        assert result["domain"] == DataDomain.ECONOMIC

    @patch('multi_agent_system.data.census_api.requests.get')
    def test_get_census_data_error(self, mock_get):
        """Test Census API error handling."""
        from multi_agent_system.data.census_api import get_census_data
        import requests
        
        mock_get.side_effect = requests.RequestException("API error")
        
        result = get_census_data("2020", "acs/acs5", use_cache=False)
        
        assert result["status"] == DataLoadStatus.ERROR
        assert result["error_type"] == DataErrorType.NETWORK


class TestOpenFEMALoader:
    """Tests for OpenFEMA API loader."""

    def test_openfema_tool_metadata_exists(self):
        """Test that OpenFEMA tool metadata is defined."""
        from multi_agent_system.data.openfema_api import OPENFEMA_TOOL_METADATA
        
        assert OPENFEMA_TOOL_METADATA["name"] == "openfema_query"
        assert OPENFEMA_TOOL_METADATA["domain"] == DataDomain.ENVIRONMENTAL
        assert OPENFEMA_TOOL_METADATA["update_frequency"] == DataUpdateFrequency.DAILY

    @patch('multi_agent_system.data.openfema_api.requests.get')
    def test_get_openfema_data_success(self, mock_get):
        """Test successful OpenFEMA API call."""
        from multi_agent_system.data.openfema_api import get_openfema_data
        
        mock_get.return_value.json.return_value = {"DisasterDeclarationsSummaries": []}
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = get_openfema_data("DisasterDeclarationsSummaries", use_cache=False)
        
        assert result["status"] == DataLoadStatus.SUCCESS
        assert result["provenance"] == DataProvenance.API
        assert result["domain"] == DataDomain.ENVIRONMENTAL

    @patch('multi_agent_system.data.openfema_api.requests.get')
    def test_get_disaster_declarations(self, mock_get):
        """Test get_disaster_declarations convenience function."""
        from multi_agent_system.data.openfema_api import get_disaster_declarations
        
        mock_get.return_value.json.return_value = {"DisasterDeclarationsSummaries": []}
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = get_disaster_declarations(state="AL", year=2024)
        
        assert result["status"] == DataLoadStatus.SUCCESS


class TestEIALoader:
    """Tests for EIA API loader."""

    def test_eia_tool_metadata_exists(self):
        """Test that EIA tool metadata is defined."""
        from multi_agent_system.data.eia_api import EIA_TOOL_METADATA
        
        assert EIA_TOOL_METADATA["name"] == "eia_query"
        assert EIA_TOOL_METADATA["domain"] == DataDomain.ECONOMIC

    @patch('multi_agent_system.data.eia_api.requests.get')
    def test_get_eia_data_success(self, mock_get):
        """Test successful EIA API call."""
        from multi_agent_system.data.eia_api import get_eia_data
        
        mock_get.return_value.json.return_value = {"series": [{"data": []}]}
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = get_eia_data("PET.RWTC.D", use_cache=False)
        
        assert result["status"] == DataLoadStatus.SUCCESS
        assert result["provenance"] == DataProvenance.API


class TestFHFALoader:
    """Tests for FHFA API loader."""

    def test_fhfa_tool_metadata_exists(self):
        """Test that FHFA tool metadata is defined."""
        from multi_agent_system.data.fhfa_api import FHFA_TOOL_METADATA
        
        assert FHFA_TOOL_METADATA["name"] == "fhfa_query"
        assert FHFA_TOOL_METADATA["domain"] == DataDomain.ECONOMIC
        assert FHFA_TOOL_METADATA["update_frequency"] == DataUpdateFrequency.QUARTERLY

    @patch('multi_agent_system.data.fhfa_api.requests.get')
    def test_get_fhfa_data_success(self, mock_get):
        """Test successful FHFA API call."""
        from multi_agent_system.data.fhfa_api import get_fhfa_data
        
        mock_get.return_value.json.return_value = {"data": []}
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = get_fhfa_data({"state": "AL"}, use_cache=False)
        
        assert result["status"] == DataLoadStatus.SUCCESS
        assert result["provenance"] == DataProvenance.API


class TestOpenETLoader:
    """Tests for OpenET API loader."""

    def test_openet_tool_metadata_exists(self):
        """Test that OpenET tool metadata is defined."""
        from multi_agent_system.data.openet_api import OPENET_TOOL_METADATA
        
        assert OPENET_TOOL_METADATA["name"] == "openet_query"
        assert OPENET_TOOL_METADATA["domain"] == DataDomain.WATER
        assert OPENET_TOOL_METADATA["access_level"] == DataAccessLevel.RESTRICTED

    def test_openet_datasource_no_api_key(self):
        """Test OpenET without API key returns permission error."""
        from multi_agent_system.data.openet_api import OpenETDataSource
        
        with patch.dict(os.environ, {"OPENET_API_KEY": ""}, clear=True):
            source = OpenETDataSource()
            source.api_key = None  # Force no API key
            
            result = source.get_et(-120.5, 38.5, "2023-01-01", "2023-12-31")
            
            assert result["status"] == DataLoadStatus.ERROR
            assert result["error_type"] == DataErrorType.PERMISSION

    @patch('multi_agent_system.data.openet_api.requests.get')
    def test_openet_get_et_success(self, mock_get):
        """Test successful OpenET API call."""
        from multi_agent_system.data.openet_api import OpenETDataSource
        
        mock_get.return_value.json.return_value = {"et": [0.5, 0.6, 0.7]}
        mock_get.return_value.raise_for_status = MagicMock()
        
        with patch.dict(os.environ, {"OPENET_API_KEY": "test_key"}):
            source = OpenETDataSource()
            source.api_key = "test_key"
            
            result = source.get_et(-120.5, 38.5, "2023-01-01", "2023-12-31", use_cache=False)
            
            assert result["status"] == DataLoadStatus.SUCCESS
            assert result["domain"] == DataDomain.WATER


class TestUSDNASSLoader:
    """Tests for USDA NASS API loader."""

    def test_usda_nass_tool_metadata_exists(self):
        """Test that USDA NASS tool metadata is defined."""
        from multi_agent_system.data.usda_nass_api import USDA_NASS_TOOL_METADATA
        
        assert USDA_NASS_TOOL_METADATA["name"] == "usda_nass_query"
        assert USDA_NASS_TOOL_METADATA["domain"] == DataDomain.AGRICULTURE

    @patch('multi_agent_system.data.usda_nass_api.requests.get')
    def test_get_nass_data_success(self, mock_get):
        """Test successful NASS API call."""
        from multi_agent_system.data.usda_nass_api import get_nass_data
        
        mock_get.return_value.json.return_value = {"data": [{"Value": "1000"}]}
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = get_nass_data({"commodity_desc": "CORN"}, use_cache=False)
        
        assert result["status"] == DataLoadStatus.SUCCESS
        assert result["domain"] == DataDomain.AGRICULTURE


class TestReturnValueStructure:
    """Tests to verify all loaders follow standardized return value structure."""

    def get_required_fields(self):
        """Get required fields for standardized return values."""
        return [
            "status",
            "data",
            "provenance",
            "update_frequency",
            "data_format",
            "access_level",
            "domain",
            "error_type",
            "error",
        ]

    @patch('multi_agent_system.data.bls_api.requests.post')
    def test_bls_has_required_fields(self, mock_post):
        """Test BLS loader returns all required fields."""
        from multi_agent_system.data.bls_api import get_bls_data
        
        mock_post.return_value.json.return_value = {}
        mock_post.return_value.raise_for_status = MagicMock()
        
        result = get_bls_data(["TEST"], "2020", "2024", use_cache=False)
        
        for field in self.get_required_fields():
            assert field in result, f"Missing field: {field}"

    @patch('multi_agent_system.data.census_api.requests.get')
    def test_census_has_required_fields(self, mock_get):
        """Test Census loader returns all required fields."""
        from multi_agent_system.data.census_api import get_census_data
        
        mock_get.return_value.json.return_value = []
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = get_census_data("2020", "acs/acs5", use_cache=False)
        
        for field in self.get_required_fields():
            assert field in result, f"Missing field: {field}"

    @patch('multi_agent_system.data.openfema_api.requests.get')
    def test_openfema_has_required_fields(self, mock_get):
        """Test OpenFEMA loader returns all required fields."""
        from multi_agent_system.data.openfema_api import get_openfema_data
        
        mock_get.return_value.json.return_value = {}
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = get_openfema_data("DisasterDeclarationsSummaries", use_cache=False)
        
        for field in self.get_required_fields():
            assert field in result, f"Missing field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
