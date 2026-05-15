#!/usr/bin/env python3
"""Quick import test for all refactored modules."""

import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestImports:
    """Test that all refactored modules import correctly."""
    
    def test_enums_import(self):
        """Test enums import from src/enums.py."""
        from enums import (
            DataLoadStatus, DataProvenance, DataUpdateFrequency,
            DataFormat, DataAccessLevel, DataDomain, DataErrorType
        )
        assert DataLoadStatus is not None
        logger.info("enums imports OK")

    def test_erddap_mcp_import(self):
        """Test erddap_mcp imports."""
        from multi_agent_system.data.erddap_mcp import get_erddap_provider, ERDDAPDataProvider
        assert get_erddap_provider is not None
        assert ERDDAPDataProvider is not None
        logger.info("erddap_mcp imports OK")

    def test_data_init_import(self):
        """Test data __init__ import."""
        from multi_agent_system.data import get_erddap_provider
        assert get_erddap_provider is not None
        logger.info("data __init__ import OK")

    def test_loader_tools_import(self):
        """Test loader_tools imports."""
        from multi_agent_system.data.loader_tools import adk_tool, LoaderMetrics
        assert adk_tool is not None
        assert LoaderMetrics is not None
        logger.info("loader_tools imports OK")

    def test_batch_orchestration_import(self):
        """Test batch_orchestration imports."""
        from multi_agent_system.data.batch_orchestration import BatchProcessor, WorkflowOrchestrator
        assert BatchProcessor is not None
        assert WorkflowOrchestrator is not None
        logger.info("batch_orchestration imports OK")

    @pytest.mark.parametrize("loader_name", [
        'bls_api', 'census_api', 'openfema_api', 'eia_api',
        'fhfa_api', 'openet_api', 'usda_nass_api'
    ])
    def test_data_loader_imports(self, loader_name):
        """Test individual data loader modules import."""
        mod = __import__(f'multi_agent_system.data.{loader_name}', fromlist=[''])
        assert mod is not None
        logger.info("%s imports OK", loader_name)

    def test_agent_cards_import(self):
        """Test AgentCards import."""
        from multi_agent_system.agents.cards import AgentCard, DATA_LOADER_AGENT_CARDS, ALL_CARDS
        assert AgentCard is not None
        assert len(DATA_LOADER_AGENT_CARDS) > 0
        assert len(ALL_CARDS) > 0
        logger.info("AgentCards: %d data loader cards, %d total", len(DATA_LOADER_AGENT_CARDS), len(ALL_CARDS))
