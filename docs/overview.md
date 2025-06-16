# System Overview

The Multi-Agent System provides a robust framework for building and managing AI agents that can work together to solve complex tasks. The system includes features for agent coordination, state management, error handling, and observability.

### Key Features

#### 1. Agent Coordination
- Hierarchical agent structure
- Inter-agent communication
- Task distribution and coordination
- State sharing and synchronization

#### 2. State Management
- Durable checkpointing system
- Granular recovery points
- Automatic state persistence
- Concurrent operation support
- Automatic cleanup of old checkpoints

#### 3. Error Handling
- Comprehensive error tracking
- Automatic retry mechanisms
- Error severity classification
- Stack trace preservation
- Recovery strategy selection

#### 4. Observability
- Pattern monitoring
- Interaction tracking
- Decision analysis
- Performance metrics
- Error analysis

### Example Usage

```python
# Initialize the system
coordinator = EnhancedCoordinator()
manager = ObservabilityManager(checkpoint_dir="checkpoints")

# Create a checkpoint with recovery point
checkpoint_id = await manager.create_checkpoint(
    agent_id="risk_analyzer",
    state={"status": "running"},
    context={"location": "New York"},
    tool_calls=[{"tool": "analyze_risks"}],
    recovery_point="pre_risk_analysis",
    metadata={"analysis_type": "comprehensive"}
)

# List available checkpoints
checkpoints = await manager.list_checkpoints(agent_id="risk_analyzer")
for checkpoint in checkpoints:
    print(f"Checkpoint {checkpoint['id']} at {checkpoint['timestamp']}")

# Restore from checkpoint if needed
checkpoint = await manager.restore_checkpoint(checkpoint_id)
if checkpoint:
    # Resume execution from checkpoint
    resume_execution(checkpoint.state, checkpoint.context)

# Clean up old checkpoints
deleted = await manager.cleanup_old_checkpoints(max_age_days=7)
print(f"Cleaned up {deleted} old checkpoints")

# Track agent interaction
metrics = manager.track_interaction(
    agent_id="risk_analyzer",
    interaction_type=InteractionType.SEQUENTIAL,
    start_time=datetime.now(),
    end_time=datetime.now() + timedelta(seconds=5),
    success=True,
    token_usage={"input": 100, "output": 50},
    context_size=1024,
    compressed_size=512
)

# Track errors
error_context = manager.track_error(
    agent_id="risk_analyzer",
    error_type="tool_failure",
    severity=ErrorSeverity.MEDIUM,
    tool_name="analyze_risks",
    context={"location": "New York"},
    stack_trace="Error in risk analysis"
)

# Analyze patterns
patterns = manager.analyze_patterns()
print(f"Success rate: {patterns['success_rate']}")
print(f"Error rate: {patterns['error_rate']}")
```

### System Architecture

The system is built with several key components:

1. **EnhancedCoordinator**: Manages agent coordination and task distribution
2. **ObservabilityManager**: Provides system observability and monitoring
3. **PatternMonitor**: Internal implementation for monitoring patterns
4. **CommunicationManager**: Handles inter-agent communication
5. **ArtifactManager**: Manages system artifacts and resources

### State Management

The system provides robust state management through:

1. **Checkpointing**:
   - Durable state persistence
   - Granular recovery points
   - Automatic cleanup
   - Concurrent operation support

2. **Error Recovery**:
   - Automatic retry mechanisms
   - Error context preservation
   - Recovery strategy selection
   - State restoration

3. **Pattern Analysis**:
   - Interaction tracking
   - Decision analysis
   - Error analysis
   - Performance metrics

### Best Practices

1. **Checkpointing**:
   - Create checkpoints at logical points in execution
   - Use meaningful recovery points
   - Include relevant metadata
   - Regular cleanup of old checkpoints

2. **Error Handling**:
   - Track all errors with context
   - Use appropriate severity levels
   - Implement retry strategies
   - Preserve stack traces

3. **Pattern Monitoring**:
   - Track all interactions
   - Monitor decision patterns
   - Analyze error patterns
   - Review performance metrics

4. **State Management**:
   - Use durable checkpoints
   - Implement recovery points
   - Clean up old checkpoints
   - Handle concurrent operations

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

The system includes a comprehensive observability framework through the `ObservabilityManager` class, which provides:

- Real-time monitoring of agent interactions and decisions
- Pattern analysis for identifying system behaviors
- Error tracking and recovery mechanisms
- Checkpoint management for state preservation
- Metrics collection for performance analysis

The `ObservabilityManager` wraps the internal `PatternMonitor` implementation while providing a cleaner, more maintainable interface for system monitoring and analysis.

Key features:
- Checkpoint creation and restoration
- Error tracking with severity levels
- Interaction and decision pattern analysis
- Token usage monitoring
- Context compression tracking
- Comprehensive metrics collection

Example usage:
```python
from src.multi_agent_system.observability import ObservabilityManager

# Initialize the manager
manager = ObservabilityManager(checkpoint_dir="checkpoints")

# Track an interaction
metrics = manager.track_interaction(
    agent_id="weather_agent",
    interaction_type=InteractionType.SEQUENTIAL,
    start_time=start_time,
    end_time=end_time,
    success=True,
    token_usage={"input": 100, "output": 50},
    context_size=1024,
    compressed_size=512
)

# Create a checkpoint
checkpoint_id = await manager.create_checkpoint(
    agent_id="weather_agent",
    state={"status": "running"},
    context={"location": "New York"},
    tool_calls=[{"tool": "weather_api"}]
)

# Track an error
error_context = manager.track_error(
    agent_id="weather_agent",
    error_type="api_error",
    severity=ErrorSeverity.MEDIUM,
    tool_name="weather_api",
    context={"location": "New York"},
    stack_trace="API timeout"
)

# Analyze patterns
analysis = manager.analyze_patterns()
```

## Getting Started
For detailed installation and setup instructions, please refer to the [Installation Guide](installation.md).

## Next Steps
- Review the [Quick Start Guide](quickstart.md) for basic usage
- Check the [Configuration Guide](configuration.md) for system setup
- Read the [User Guide](user-guide.md) for detailed usage instructions
- Consult the [API Reference](api-reference.md) for technical details 