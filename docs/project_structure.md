# Project Structure

## Overview
This project implements a multi-agent system for climate risk analysis with ADK features. The system uses a modular architecture with clear separation of concerns and robust error handling.

## Directory Structure

```
src/
├── multi_agent_system/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── risk_agents.py
│   │   └── cards.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── risk_workflow.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── error_handling.py
│   │   ├── agent_tools.py
│   │   └── adk_features.py
│   ├── data_management.py
│   ├── agent_communication.py
│   ├── session_manager.py
│   ├── weather_risks.py
│   ├── risk_definitions.py
│   └── adk_integration.py
├── tests/
│   ├── __init__.py
│   ├── test_risk_workflow.py
│   ├── test_risk_agents.py
│   └── test_error_handling.py
└── docs/
    ├── implementation_guide.md
    └── project_structure.md
```

## Core Components

### 1. Agent System
- **Base Agent** (`agents/base_agent.py`): Core agent implementation with ADK features
- **Risk Agents** (`agents/risk_agents.py`): Specialized agents for risk analysis
- **Agent Cards** (`agents/cards.py`): Agent capability definitions

### 2. Workflow System
- **Risk Workflow** (`workflows/risk_workflow.py`): Orchestrates risk analysis process
- **Workflow Steps**:
  1. Address Validation
  2. Historical Analysis
  3. Risk Analysis
  4. Investment Impact Analysis
  5. Report Generation

### 3. Data Management
- **Data Manager** (`data_management.py`): Handles data operations with ADK features
- **Features**:
  - Caching
  - Parallel Processing
  - Error Handling
  - Metrics Collection

### 4. Agent Communication
- **Message System** (`agent_communication.py`): Manages inter-agent communication
- **Features**:
  - Message Routing
  - Buffering
  - Parallel Processing
  - Metrics Collection

### 5. Session Management
- **Session Manager** (`session_manager.py`): Manages analysis sessions
- **Features**:
  - Session Tracking
  - State Management
  - Metrics Collection
  - Resource Management

### 6. Risk Analysis
- **Weather Risks** (`weather_risks.py`): Analyzes climate risks
- **Risk Definitions** (`risk_definitions.py`): Standardized risk definitions
- **ADK Integration** (`adk_integration.py`): ADK feature integration

### 7. Utilities
- **Error Handling** (`utils/error_handling.py`): Comprehensive error handling
- **Agent Tools** (`utils/agent_tools.py`): Common agent utilities
- **ADK Features** (`utils/adk_features.py`): ADK feature implementations

## ADK Features

### 1. Performance Optimization
- Metrics Collection
- Caching
- Parallel Processing
- Resource Management

### 2. Reliability
- Circuit Breaker
- Error Handling
- Buffering
- Retry Mechanisms

### 3. Monitoring
- Performance Metrics
- Resource Usage
- Operation Tracking
- State Monitoring

### 4. Data Management
- Caching
- Validation
- Parallel Processing
- Error Handling

## Testing

### 1. Unit Tests
- Agent Tests
- Workflow Tests
- Error Handling Tests

### 2. Integration Tests
- End-to-End Tests
- Performance Tests
- Reliability Tests

## Documentation

### 1. Implementation Guide
- Architecture Overview
- Component Details
- Usage Examples
- Best Practices

### 2. Project Structure
- Directory Layout
- Component Descriptions
- Feature Overview
- Testing Strategy 