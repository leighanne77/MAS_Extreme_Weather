#!/usr/bin/env python3
# filepath: /Users/midnighthome/Builds/004_MAS_Climate/tests/test_imports.py
"""Quick import test for all refactored modules."""
import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestModuleImports:
    """Test that all refactored modules import correctly."""
    
    def test_enums_import(self):
        """Test enums import."""
        from enums import DataLoadStatus, DataProvenance, DataDomain
        assert DataLoadStatus is not None
        assert DataProvenance is not None
        assert DataDomain is not None
        logger.info("enums imports OK")
    
    def test_loader_tools_import(self):
        """Test loader_tools import."""
        from multi_agent_system.data.loader_tools import LoaderMetrics, adk_tool, DataLoaderAgentCard
        assert LoaderMetrics is not None
        assert adk_tool is not None
        assert DataLoaderAgentCard is not None
        logger.info("loader_tools imports OK")
    
    def test_batch_orchestration_import(self):
        """Test batch_orchestration import."""
        from multi_agent_system.data.batch_orchestration import WorkflowStep, StepResult, WorkflowResult
        assert WorkflowStep is not None
        assert StepResult is not None
        assert WorkflowResult is not None
        logger.info("batch_orchestration imports OK")
    
    def test_bls_api_import(self):
        """Test bls_api import."""
        from multi_agent_system.data.bls_api import get_bls_data, BLS_TOOL_METADATA
        assert get_bls_data is not None
        assert BLS_TOOL_METADATA is not None
        logger.info("bls_api imports OK")
    
    def test_census_api_import(self):
        """Test census_api import."""
        from multi_agent_system.data.census_api import get_census_data, CENSUS_TOOL_METADATA
        assert get_census_data is not None
        assert CENSUS_TOOL_METADATA is not None
        logger.info("census_api imports OK")
    
    def test_openfema_api_import(self):
        """Test openfema_api import."""
        from multi_agent_system.data.openfema_api import get_openfema_data, OPENFEMA_TOOL_METADATA
        assert get_openfema_data is not None
        assert OPENFEMA_TOOL_METADATA is not None
        logger.info("openfema_api imports OK")
    
    def test_eia_api_import(self):
        """Test eia_api import."""
        from multi_agent_system.data.eia_api import get_eia_data, EIA_TOOL_METADATA
        assert get_eia_data is not None
        assert EIA_TOOL_METADATA is not None
        logger.info("eia_api imports OK")
    
    def test_fhfa_api_import(self):
        """Test fhfa_api import."""
        from multi_agent_system.data.fhfa_api import get_fhfa_data, FHFA_TOOL_METADATA
        assert get_fhfa_data is not None
        assert FHFA_TOOL_METADATA is not None
        logger.info("fhfa_api imports OK")
    
    def test_openet_api_import(self):
        """Test openet_api import."""
        from multi_agent_system.data.openet_api import OpenETDataSource, OPENET_TOOL_METADATA
        assert OpenETDataSource is not None
        assert OPENET_TOOL_METADATA is not None
        logger.info("openet_api imports OK")
    
    def test_usda_nass_api_import(self):
        """Test usda_nass_api import."""
        from multi_agent_system.data.usda_nass_api import get_nass_data, USDA_NASS_TOOL_METADATA
        assert get_nass_data is not None
        assert USDA_NASS_TOOL_METADATA is not None
        logger.info("usda_nass_api imports OK")
    
    def test_agent_cards_import(self):
        """Test agent cards import."""
        from multi_agent_system.agents.cards import DATA_LOADER_AGENT_CARDS, ALL_AGENT_CARDS
        assert len(DATA_LOADER_AGENT_CARDS) > 0
        assert len(ALL_AGENT_CARDS) > 0
        logger.info("AgentCards: %d data loader cards, %d total", len(DATA_LOADER_AGENT_CARDS), len(ALL_AGENT_CARDS))
