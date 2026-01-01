#!/usr/bin/env python3
"""Test imports for all refactored modules."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print('Testing imports...\n')

# Test 1: enums
try:
    from enums import DataLoadStatus, DataProvenance, DataUpdateFrequency
    print('✅ enums imports OK')
except Exception as e:
    print(f'❌ enums import failed: {e}')

# Test 2: data loaders
loaders = ['bls_api', 'census_api', 'openfema_api', 'eia_api', 'fhfa_api', 'openet_api', 'usda_nass_api']
for loader in loaders:
    try:
        mod = __import__(f'multi_agent_system.data.{loader}', fromlist=[''])
        print(f'✅ {loader} imports OK')
    except Exception as e:
        print(f'❌ {loader} import failed: {e}')

# Test 3: loader_tools
try:
    from multi_agent_system.data.loader_tools import LoaderMetrics, DataLoaderAgentCard
    print('✅ loader_tools imports OK')
except Exception as e:
    print(f'❌ loader_tools import failed: {e}')

# Test 4: batch_orchestration
try:
    from multi_agent_system.data.batch_orchestration import WorkflowOrchestrator
    print('✅ batch_orchestration imports OK')
except Exception as e:
    print(f'❌ batch_orchestration import failed: {e}')

# Test 5: agents/cards
try:
    from multi_agent_system.agents.cards import DATA_LOADER_AGENT_CARDS
    print(f'✅ agents/cards imports OK ({len(DATA_LOADER_AGENT_CARDS)} loader cards)')
except Exception as e:
    print(f'❌ agents/cards import failed: {e}')

# Test 6: communication
try:
    from multi_agent_system.communication import CommunicationManager, SharedState
    print('✅ communication imports OK')
except Exception as e:
    print(f'❌ communication import failed: {e}')

print('\nImport test complete!')
