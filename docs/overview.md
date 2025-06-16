# System Overview

This document provides a high-level overview of the Multi-Agent Climate Risk Analysis System.

> **Note:** The codebase uses a `src/` layout. All core modules are in `src/multi_agent_system/`.

## Introduction
The Multi-Agent Climate Risk Analysis System is a sophisticated system for comprehensive climate risk analysis, featuring specialized agents for different aspects of risk assessment and management.

## Key Features
- Multi-agent architecture for climate risk analysis
- Advanced state management and error recovery
- Real-time and historical data integration
- Modular, extensible, and observable

### Performance Optimization
- **Efficient Caching System**
  - Configurable cache durations for different types of data
  - Automatic cache invalidation based on data freshness requirements
  - Smart caching for frequently accessed data
  - Reduced API calls and database queries

### Personalized User Experience
- **User Preference Management**
  - Language preferences
  - Unit system preferences (metric/imperial)
  - Location-based customization
  - Historical interaction tracking
  - Personalized recommendations

### Advanced State Management
- **Robust Session Handling**
  - Persistent session state
  - Context-aware operations
  - State synchronization across agents
  - Efficient state updates
  - Automatic state cleanup

### Resource Efficiency
- **Optimized Resource Usage**
  - Concurrent task execution
  - Smart data caching
  - Efficient memory management
  - Reduced redundant operations
  - Optimized API calls

### Comprehensive Error Handling
- **Robust Error Management**
  - Graceful error recovery
  - Detailed error logging
  - Automatic retry mechanisms
  - User-friendly error messages
  - State preservation during errors

## System Architecture

The system is organized as follows:

```
project-root/
│
├── src/
│   └── multi_agent_system/
│       ├── agent_team.py
│       ├── agent_functions.py
│       ├── enhanced_coordinator.py
│       ├── communication.py
│       ├── artifact_manager.py
│       ├── workflows.py
│       ├── adk_integration.py
│       ├── session_manager.py
│       ├── risk_definitions.py
│       ├── weather_risks.py
│       └── observability.py
├── tests/
├── docs/
└── ...
```

## Example Usage

```python
from src.multi_agent_system.agent_team import AgentTeam
from google.adk.agents import Agent
```

## Specialized Agents
- **Risk Analyzer**: Assesses climate risks using real-time and historical data
- **Data Collector**: Gathers and validates weather and risk data
- **Report Generator**: Produces actionable reports

## Architecture Decision

### Hybrid Approach: Custom Core + ADK Coordination
We have chosen a hybrid architecture that combines our custom implementation with Google's Agent Development Kit (ADK) for the following reasons:

1. **Core Components (Custom)**
   - Climate-specific risk analysis logic
   - Weather data caching and processing
   - Specialized agent functions for climate analysis
   - Custom session management for climate data

2. **Agent Coordination (ADK)**
   - Multi-agent system orchestration
   - Event handling and communication
   - Workflow management
   - Session state management

## Observability and Error Recovery

### State Management
- Durable state management through checkpoints
- Automatic state persistence and restoration
- Context preservation across function calls
- Function call history tracking

### Error Handling
- Graceful error handling with severity-based recovery
- Automatic rollback to last known good state
- Detailed error context for debugging
- Configurable recovery strategies

## Getting Started
For detailed installation and setup instructions, please refer to the [Installation Guide](installation.md).

## Next Steps
- Review the [Quick Start Guide](quickstart.md) for basic usage
- Check the [Configuration Guide](configuration.md) for system setup
- Read the [User Guide](user-guide.md) for detailed usage instructions
- Consult the [API Reference](api-reference.md) for technical details 