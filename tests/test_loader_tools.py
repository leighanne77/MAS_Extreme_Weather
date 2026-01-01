#!/usr/bin/env python3
# filepath: /Users/midnighthome/Builds/004_MAS_Climate/tests/test_loader_tools.py
"""
Tests for loader_tools.py - ADK tool decorators and metrics collection.

Tests cover:
- LoaderMetrics dataclass
- adk_tool decorator
- DataLoaderAgentCard class
- Card registration and retrieval
"""
import sys
import os
import time

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

from multi_agent_system.data.loader_tools import (
    LoaderMetrics,
    adk_tool,
    DataLoaderAgentCard,
    get_loader_metrics,
    register_data_loader_card,
    get_all_data_loader_cards,
    DATA_LOADER_CARDS,
)


class TestLoaderMetrics:
    """Tests for LoaderMetrics dataclass."""

    def test_initial_state(self):
        """Test initial metrics state."""
        metrics = LoaderMetrics()
        assert metrics.call_count == 0
        assert metrics.error_count == 0
        assert metrics.total_latency_ms == 0.0
        assert metrics.last_call_time is None
        assert metrics.last_error is None

    def test_record_successful_call(self):
        """Test recording a successful call."""
        metrics = LoaderMetrics()
        metrics.record_call(latency_ms=150.0)
        
        assert metrics.call_count == 1
        assert metrics.error_count == 0
        assert metrics.total_latency_ms == 150.0
        assert metrics.last_call_time is not None
        assert metrics.last_error is None

    def test_record_failed_call(self):
        """Test recording a failed call."""
        metrics = LoaderMetrics()
        metrics.record_call(latency_ms=100.0, error="Connection timeout")
        
        assert metrics.call_count == 1
        assert metrics.error_count == 1
        assert metrics.total_latency_ms == 100.0
        assert metrics.last_error == "Connection timeout"

    def test_avg_latency(self):
        """Test average latency calculation."""
        metrics = LoaderMetrics()
        metrics.record_call(latency_ms=100.0)
        metrics.record_call(latency_ms=200.0)
        metrics.record_call(latency_ms=300.0)
        
        assert metrics.avg_latency_ms == 200.0

    def test_avg_latency_zero_calls(self):
        """Test average latency with no calls."""
        metrics = LoaderMetrics()
        assert metrics.avg_latency_ms == 0.0

    def test_error_rate(self):
        """Test error rate calculation."""
        metrics = LoaderMetrics()
        metrics.record_call(latency_ms=100.0)
        metrics.record_call(latency_ms=100.0, error="Error 1")
        metrics.record_call(latency_ms=100.0)
        metrics.record_call(latency_ms=100.0, error="Error 2")
        
        assert metrics.error_rate == 0.5

    def test_error_rate_zero_calls(self):
        """Test error rate with no calls."""
        metrics = LoaderMetrics()
        assert metrics.error_rate == 0.0

    def test_to_dict(self):
        """Test conversion to dict."""
        metrics = LoaderMetrics()
        metrics.record_call(latency_ms=100.0)
        metrics.record_call(latency_ms=200.0, error="Test error")
        
        result = metrics.to_dict()
        
        assert result["call_count"] == 2
        assert result["error_count"] == 1
        assert result["avg_latency_ms"] == 150.0
        assert result["error_rate"] == 0.5
        assert result["last_call_time"] is not None


class TestAdkToolDecorator:
    """Tests for the @adk_tool decorator."""

    def test_decorator_adds_metadata(self):
        """Test that decorator adds metadata to function."""
        @adk_tool(
            name="test_tool",
            description="A test tool",
            domain=DataDomain.ECONOMIC,
            update_frequency=DataUpdateFrequency.DAILY,
        )
        def my_tool(x: int) -> dict:
            return {"status": DataLoadStatus.SUCCESS, "data": x * 2}
        
        assert hasattr(my_tool, "_adk_tool_metadata")
        assert my_tool._adk_tool_metadata["name"] == "test_tool"
        assert my_tool._adk_tool_metadata["domain"] == DataDomain.ECONOMIC

    def test_decorator_preserves_function_result(self):
        """Test that decorator preserves original function result."""
        @adk_tool(
            name="test_tool_2",
            description="A test tool",
            domain=DataDomain.AGRICULTURE,
            update_frequency=DataUpdateFrequency.WEEKLY,
        )
        def my_tool(x: int) -> dict:
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": x * 2,
                "provenance": DataProvenance.API,
            }
        
        result = my_tool(5)
        assert result["data"] == 10
        assert result["status"] == DataLoadStatus.SUCCESS

    def test_decorator_adds_metrics(self):
        """Test that decorator adds metrics to result."""
        @adk_tool(
            name="test_tool_3",
            description="A test tool",
            domain=DataDomain.WATER,
            update_frequency=DataUpdateFrequency.DAILY,
        )
        def my_tool() -> dict:
            return {"status": DataLoadStatus.SUCCESS, "data": "test"}
        
        result = my_tool()
        assert "metrics" in result
        assert result["metrics"]["call_count"] >= 1

    def test_decorator_handles_exceptions(self):
        """Test that decorator handles exceptions gracefully."""
        @adk_tool(
            name="test_tool_4",
            description="A failing tool",
            domain=DataDomain.ECONOMIC,
            update_frequency=DataUpdateFrequency.DAILY,
        )
        def failing_tool() -> dict:
            raise ValueError("Test exception")
        
        result = failing_tool()
        assert result["status"] == DataLoadStatus.ERROR
        assert result["error_type"] == DataErrorType.UNKNOWN
        assert "Test exception" in result["error"]

    def test_decorator_tracks_metrics(self):
        """Test that metrics are tracked across calls."""
        @adk_tool(
            name="test_tool_5",
            description="A test tool",
            domain=DataDomain.ECONOMIC,
            update_frequency=DataUpdateFrequency.DAILY,
        )
        def my_tool() -> dict:
            return {"status": DataLoadStatus.SUCCESS, "data": "test"}
        
        # Make multiple calls
        my_tool()
        my_tool()
        result = my_tool()
        
        metrics = get_loader_metrics("test_tool_5")
        assert metrics.call_count >= 3


class TestDataLoaderAgentCard:
    """Tests for DataLoaderAgentCard class."""

    def test_card_creation(self):
        """Test creating a DataLoaderAgentCard."""
        card = DataLoaderAgentCard(
            name="test_loader",
            description="A test loader",
            version="1.0.0",
            domain=DataDomain.ECONOMIC,
            update_frequency=DataUpdateFrequency.DAILY,
            access_level=DataAccessLevel.PUBLIC,
            data_format=DataFormat.JSON,
        )
        
        assert card.name == "test_loader"
        assert card.domain == DataDomain.ECONOMIC
        assert card.access_level == DataAccessLevel.PUBLIC

    def test_to_agent_card_dict(self):
        """Test conversion to AgentCard-compatible dict."""
        card = DataLoaderAgentCard(
            name="test_loader_2",
            description="A test loader",
            version="2.0.0",
            domain=DataDomain.AGRICULTURE,
            update_frequency=DataUpdateFrequency.WEEKLY,
            access_level=DataAccessLevel.RESTRICTED,
            data_format=DataFormat.CSV,
            skills=[
                {
                    "name": "load_data",
                    "description": "Load some data",
                    "parameters": {"file": {"type": "string"}},
                }
            ],
        )
        
        result = card.to_agent_card_dict()
        
        assert result["name"] == "test_loader_2"
        assert result["version"] == "2.0.0"
        assert result["capabilities"]["data_loading"] is True
        assert result["capabilities"]["caching"] is True
        assert result["metadata"]["domain"] == DataDomain.AGRICULTURE.value
        assert len(result["skills"]) == 1


class TestCardRegistration:
    """Tests for card registration functions."""

    def test_register_card(self):
        """Test registering a new card."""
        card = DataLoaderAgentCard(
            name="new_test_loader",
            description="A new test loader",
            version="1.0.0",
            domain=DataDomain.WATER,
            update_frequency=DataUpdateFrequency.HOURLY,
            access_level=DataAccessLevel.PUBLIC,
            data_format=DataFormat.JSON,
        )
        
        register_data_loader_card(card)
        
        assert "new_test_loader" in DATA_LOADER_CARDS
        assert DATA_LOADER_CARDS["new_test_loader"] == card

    def test_get_all_cards(self):
        """Test getting all registered cards."""
        cards = get_all_data_loader_cards()
        
        assert isinstance(cards, list)
        assert len(cards) > 0
        
        # Each card should be a dict
        for card in cards:
            assert isinstance(card, dict)
            assert "name" in card
            assert "capabilities" in card

    def test_pre_registered_cards_exist(self):
        """Test that pre-registered cards exist."""
        # These should be registered on module load
        assert "ers_data_loader" in DATA_LOADER_CARDS
        assert "nass_data_loader" in DATA_LOADER_CARDS
        assert "bls_data_loader" in DATA_LOADER_CARDS
        assert "census_data_loader" in DATA_LOADER_CARDS
        assert "openfema_data_loader" in DATA_LOADER_CARDS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
