#!/usr/bin/env python3
"""Quick import test for all refactored modules."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    errors = []
    
    print("Testing imports...")
    
    # Test enums
    try:
        from enums import DataLoadStatus, DataProvenance, DataUpdateFrequency, DataFormat, DataAccessLevel, DataDomain, DataErrorType
        print("✅ enums imports OK")
    except Exception as e:
        errors.append(f"enums: {e}")
        print(f"❌ enums: {e}")

    # Test erddap_mcp
    try:
        from multi_agent_system.data.erddap_mcp import get_erddap_provider, ERDDAPDataProvider
        print("✅ erddap_mcp imports OK")
    except Exception as e:
        errors.append(f"erddap_mcp: {e}")
        print(f"❌ erddap_mcp: {e}")

    # Test data __init__
    try:
        from multi_agent_system.data import get_erddap_provider
        print("✅ data __init__ import OK")
    except Exception as e:
        errors.append(f"data __init__: {e}")
        print(f"❌ data __init__: {e}")

    # Test loader_tools
    try:
        from multi_agent_system.data.loader_tools import adk_tool, LoaderMetrics
        print("✅ loader_tools imports OK")
    except Exception as e:
        errors.append(f"loader_tools: {e}")
        print(f"❌ loader_tools: {e}")

    # Test batch_orchestration
    try:
        from multi_agent_system.data.batch_orchestration import BatchProcessor, WorkflowOrchestrator
        print("✅ batch_orchestration imports OK")
    except Exception as e:
        errors.append(f"batch_orchestration: {e}")
        print(f"❌ batch_orchestration: {e}")

    # Test data loaders
    loaders = ['bls_api', 'census_api', 'openfema_api', 'eia_api', 'fhfa_api', 'openet_api', 'usda_nass_api']
    for loader in loaders:
        try:
            mod = __import__(f'multi_agent_system.data.{loader}', fromlist=[''])
            print(f"✅ {loader} imports OK")
        except Exception as e:
            errors.append(f"{loader}: {e}")
            print(f"❌ {loader}: {e}")

    # Test AgentCards
    try:
        from multi_agent_system.agents.cards import AgentCard, DATA_LOADER_AGENT_CARDS, ALL_CARDS
        print(f"✅ AgentCards: {len(DATA_LOADER_AGENT_CARDS)} data loader cards, {len(ALL_CARDS)} total")
    except Exception as e:
        errors.append(f"AgentCards: {e}")
        print(f"❌ AgentCards: {e}")

    print("\n" + "="*50)
    if errors:
        print(f"❌ {len(errors)} import errors found")
        for err in errors:
            print(f"  - {err}")
        return 1
    else:
        print("✅ All imports successful!")
        return 0

if __name__ == "__main__":
    sys.exit(test_imports())
