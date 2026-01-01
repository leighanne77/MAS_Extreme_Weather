#!/usr/bin/env python3
# filepath: /Users/midnighthome/Builds/004_MAS_Climate/tests/test_imports.py
"""Quick import test for all refactored modules."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test all module imports."""
    errors = []
    
    # Test enums
    try:
        from enums import DataLoadStatus, DataProvenance, DataDomain
        print("✅ enums imports OK")
    except Exception as e:
        errors.append(f"enums: {e}")
        print(f"❌ enums: {e}")
    
    # Test loader_tools
    try:
        from multi_agent_system.data.loader_tools import LoaderMetrics, adk_tool, DataLoaderAgentCard
        print("✅ loader_tools imports OK")
    except Exception as e:
        errors.append(f"loader_tools: {e}")
        print(f"❌ loader_tools: {e}")
    
    # Test batch_orchestration
    try:
        from multi_agent_system.data.batch_orchestration import WorkflowStep, StepResult, WorkflowResult
        print("✅ batch_orchestration imports OK")
    except Exception as e:
        errors.append(f"batch_orchestration: {e}")
        print(f"❌ batch_orchestration: {e}")
    
    # Test bls_api
    try:
        from multi_agent_system.data.bls_api import get_bls_data, BLS_TOOL_METADATA
        print("✅ bls_api imports OK")
    except Exception as e:
        errors.append(f"bls_api: {e}")
        print(f"❌ bls_api: {e}")
    
    # Test census_api
    try:
        from multi_agent_system.data.census_api import get_census_data, CENSUS_TOOL_METADATA
        print("✅ census_api imports OK")
    except Exception as e:
        errors.append(f"census_api: {e}")
        print(f"❌ census_api: {e}")
    
    # Test openfema_api
    try:
        from multi_agent_system.data.openfema_api import get_openfema_data, OPENFEMA_TOOL_METADATA
        print("✅ openfema_api imports OK")
    except Exception as e:
        errors.append(f"openfema_api: {e}")
        print(f"❌ openfema_api: {e}")
    
    # Test eia_api
    try:
        from multi_agent_system.data.eia_api import get_eia_data, EIA_TOOL_METADATA
        print("✅ eia_api imports OK")
    except Exception as e:
        errors.append(f"eia_api: {e}")
        print(f"❌ eia_api: {e}")
    
    # Test fhfa_api
    try:
        from multi_agent_system.data.fhfa_api import get_fhfa_data, FHFA_TOOL_METADATA
        print("✅ fhfa_api imports OK")
    except Exception as e:
        errors.append(f"fhfa_api: {e}")
        print(f"❌ fhfa_api: {e}")
    
    # Test openet_api
    try:
        from multi_agent_system.data.openet_api import OpenETDataSource, OPENET_TOOL_METADATA
        print("✅ openet_api imports OK")
    except Exception as e:
        errors.append(f"openet_api: {e}")
        print(f"❌ openet_api: {e}")
    
    # Test usda_nass_api
    try:
        from multi_agent_system.data.usda_nass_api import get_nass_data, USDA_NASS_TOOL_METADATA
        print("✅ usda_nass_api imports OK")
    except Exception as e:
        errors.append(f"usda_nass_api: {e}")
        print(f"❌ usda_nass_api: {e}")
    
    # Test agent cards
    try:
        from multi_agent_system.agents.cards import DATA_LOADER_AGENT_CARDS, ALL_AGENT_CARDS
        print(f"✅ AgentCards: {len(DATA_LOADER_AGENT_CARDS)} data loader cards, {len(ALL_AGENT_CARDS)} total")
    except Exception as e:
        errors.append(f"cards: {e}")
        print(f"❌ cards: {e}")
    
    print("\n" + "="*50)
    if errors:
        print(f"❌ {len(errors)} import errors found")
        return False
    else:
        print("✅ All imports successful!")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
