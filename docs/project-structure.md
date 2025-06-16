# Multi-Agent Climate Risk Analysis System

## Project Overview

This project implements a comprehensive multi-agent system for climate risk analysis, combining specialized agents, workflow management, and advanced coordination capabilities.

## Directory Structure

> **Note:** The project uses a `src/` layout. All core code is in `src/multi_agent_system/`.

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

## Main Packages
- **src.multi_agent_system**: All core modules and logic
- **tests/**: Unit and integration tests
- **docs/**: Documentation

## Example Import
```python
from src.multi_agent_system.agent_team import AgentTeam
from google.adk.agents import Agent
```

## Notes
- All new modules should be placed in `src/multi_agent_system/`.
- Tests should import from `src.multi_agent_system`.
- The `src/` layout helps avoid import conflicts and makes the project structure clearer.

## Function-Based Tools

When you assign a regular Python function to an agent's tools list, the ADK framework automatically wraps it as a Function Tool for you. This approach offers flexibility and quick integration.

### Parameters

Define your function parameters using standard JSON-serializable types (e.g., string, integer, list, dictionary). It's important to avoid setting default values for parameters, as the language model (LLM) does not currently support interpreting them.

## Core Components

### 1. Agent Team (`agent_team.py`)
- Manages agent coordination and execution
- Handles agent state and communication
- Implements agent lifecycle management
- Provides error handling and recovery

### 2. Enhanced Coordinator (`enhanced_coordinator.py`)
- Orchestrates task execution
- Manages parallel processing
- Handles token usage tracking
- Implements context compression

### 3. Communication Manager (`communication.py`)
- Manages inter-agent messaging
- Handles state synchronization
- Implements error propagation
- Provides heartbeat monitoring

### 4. Artifact Manager (`artifact_manager.py`)
- Manages output storage
- Implements version control
- Handles cleanup policies
- Provides access control

### 5. Workflow Manager (`workflows.py`)
- Orchestrates processes
- Tracks state transitions
- Handles error recovery
- Monitors progress

### 6. Observability System (`observability.py`)
- Tracks performance metrics
- Monitors error patterns
- Analyzes agent interactions
- Reports system health

### 7. ADK Integration (`adk_integration.py`)
- Manages external service communication
- Handles response processing
- Implements error management
- Provides configuration control

## Configuration

### Agent Configuration
- Model settings
- Retry policies
- Timeout values
- Resource limits

### Coordinator Configuration
- Parallel execution settings
- Token usage limits
- Context compression settings
- Error handling policies

### Communication Configuration
- Message timeouts
- Retry policies
- State sync intervals
- Heartbeat settings

### Storage Configuration
- Base directory
- Cleanup policies
- Access controls
- Version settings

### Logging Configuration
- Log levels
- Output formats
- Rotation policies
- Error tracking

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document all public interfaces
- Include usage examples

### Testing
- Write unit tests for all components
- Include integration tests
- Maintain test coverage
- Document test scenarios

### Documentation
- Maintain comprehensive docstrings
- Update README files
- Document configuration options
- Include usage examples

### Error Handling
- Implement proper error types
- Include error recovery
- Log error details
- Provide error context

## Dependencies

### Core Dependencies
- asyncio: Async operations
- aiohttp: HTTP requests
- logging: System logging
- typing: Type hints
- json: Data serialization

### Development Dependencies
- pytest: Testing framework
- black: Code formatting
- mypy: Type checking
- pylint: Code analysis

## Version Information

Current Version: 1.0.0

### Version History
- 1.0.0: Initial release
  - Core multi-agent system
  - Basic workflow management
  - Initial ADK integration
  - Basic observability 