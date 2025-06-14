# Data Definitions

## Overview

This document defines the key data structures and types used in the Multi-Agent Climate Risk Analysis System.

## Core Data Structures

### 1. Agent State
```python
class AgentState:
    agent_id: str
    status: AgentStatus
    current_task: Optional[Task]
    error: Optional[Exception]
    metrics: Dict[str, Any]
```

### 2. Shared State
```python
class SharedState:
    session_id: str
    agents: Dict[str, AgentState]
    artifacts: Dict[str, Artifact]
    workflow_state: WorkflowState
    error_context: Optional[ErrorContext]
```

### 3. Workflow State
```python
class WorkflowState:
    workflow_id: str
    current_step: str
    completed_steps: List[str]
    results: Dict[str, Any]
    error: Optional[Exception]
    created_at: datetime
```

### 4. Artifact
```python
class Artifact:
    artifact_id: str
    type: str
    data: Any
    metadata: Dict[str, Any]
    created_at: datetime
    version: int
```

### 5. Error Context
```python
class ErrorContext:
    error_type: str
    message: str
    stack_trace: str
    context: Dict[str, Any]
    severity: ErrorSeverity
```

## Message Types

### 1. Control Messages
```python
class ControlMessage:
    message_type: MessageType
    sender_id: str
    recipient_id: str
    payload: Dict[str, Any]
    timestamp: datetime
```

### 2. Data Messages
```python
class DataMessage:
    message_type: MessageType
    sender_id: str
    recipient_id: str
    data: Any
    metadata: Dict[str, Any]
    timestamp: datetime
```

### 3. State Messages
```python
class StateMessage:
    message_type: MessageType
    sender_id: str
    state: AgentState
    timestamp: datetime
```

### 4. Error Messages
```python
class ErrorMessage:
    message_type: MessageType
    sender_id: str
    error: ErrorContext
    timestamp: datetime
```

### 5. Heartbeat Messages
```python
class HeartbeatMessage:
    message_type: MessageType
    sender_id: str
    status: AgentStatus
    timestamp: datetime
```

## Metrics and Monitoring

### 1. Interaction Metrics
```python
class InteractionMetrics:
    total_interactions: int
    successful_interactions: int
    failed_interactions: int
    average_response_time: float
    error_rate: float
```

### 2. Decision Metrics
```python
class DecisionMetrics:
    total_decisions: int
    correct_decisions: int
    incorrect_decisions: int
    confidence_scores: List[float]
    decision_times: List[float]
```

### 3. Performance Metrics
```python
class PerformanceMetrics:
    cpu_usage: float
    memory_usage: float
    response_times: List[float]
    throughput: float
    error_rate: float
```

## Configuration Types

### 1. Agent Configuration
```python
class AgentConfig:
    model_name: str
    max_retries: int
    timeout: int
    resource_limits: Dict[str, Any]
```

### 2. Coordinator Configuration
```python
class CoordinatorConfig:
    max_parallel_tasks: int
    token_limit: int
    compression_threshold: int
    error_policy: ErrorPolicy
```

### 3. Communication Configuration
```python
class CommunicationConfig:
    message_timeout: int
    retry_policy: RetryPolicy
    sync_interval: int
    heartbeat_interval: int
```

### 4. Storage Configuration
```python
class StorageConfig:
    base_directory: str
    cleanup_policy: CleanupPolicy
    access_control: AccessControl
    version_control: VersionControl
```

## Enums and Constants

### 1. Agent Status
```python
class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
```

### 2. Message Type
```python
class MessageType(Enum):
    CONTROL = "control"
    DATA = "data"
    STATE = "state"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
```

### 3. Error Severity
```python
class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

### 4. Workflow Status
```python
class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

## Type Aliases

```python
# Common type aliases
AgentID = str
SessionID = str
WorkflowID = str
ArtifactID = str
MessageID = str

# Configuration type aliases
ConfigDict = Dict[str, Any]
StateDict = Dict[str, Any]
MetricsDict = Dict[str, Any]
```

## Usage Examples

### 1. Creating Agent State
```python
state = AgentState(
    agent_id="risk_analyzer",
    status=AgentStatus.IDLE,
    current_task=None,
    error=None,
    metrics={}
)
```

### 2. Sending Control Message
```python
message = ControlMessage(
    message_type=MessageType.CONTROL,
    sender_id="coordinator",
    recipient_id="risk_analyzer",
    payload={"action": "start_analysis"},
    timestamp=datetime.utcnow()
)
```

### 3. Updating Workflow State
```python
workflow_state = WorkflowState(
    workflow_id="analysis_123",
    current_step="data_collection",
    completed_steps=["setup"],
    results={"setup": "completed"},
    error=None,
    created_at=datetime.utcnow()
)
```

### 4. Recording Metrics
```python
metrics = InteractionMetrics(
    total_interactions=100,
    successful_interactions=95,
    failed_interactions=5,
    average_response_time=0.5,
    error_rate=0.05
)
```

## Risk Definitions

Risk definitions are standardized from major governmental and insurance providers:

- **FEMA (Federal Emergency Management Agency)**
- **ISO (Insurance Services Office)**
- **WHO (World Health Organization)**
- **NOAA (National Oceanic and Atmospheric Administration)**

Each risk type (flooding, wildfire, extreme storms, extreme heat) has high and medium severity thresholds.

### Consensus Thresholds

Consensus thresholds combine multiple sources:

- **Flooding**:
  - High: 50.0 mm rainfall in 1 hour
  - Medium: 20.0 mm rainfall in 1 hour

- **Wildfire**:
  - High: Temperature > 35.0°C, Humidity < 20%, Wind Speed > 13.4 m/s
  - Medium: Temperature > 30.0°C, Humidity < 30%, Wind Speed > 8.9 m/s

- **Extreme Storms**:
  - High: Wind Speed > 25.7 m/s
  - Medium: Wind Speed > 17.9 m/s

- **Extreme Heat**:
  - High: Temperature > 40.6°C
  - Medium: Temperature > 37.8°C

## Data Sources

### FEMA (Federal Emergency Management Agency)
- **Purpose:** Provides definitions for flooding, wildfire, extreme storms, and extreme heat.
- **URL:** [FEMA Flood Maps](https://www.fema.gov/flood-maps)

### ISO (Insurance Services Office)
- **Purpose:** Provides definitions for flooding, wildfire, extreme storms, and extreme heat.
- **URL:** [ISO Property Evaluation Schedule](https://www.iso.com/)

### WHO (World Health Organization)
- **Purpose:** Provides definitions for extreme heat.
- **URL:** [WHO Heat Health Action Plans](https://www.who.int/health-topics/heatwaves)

### NOAA (National Oceanic and Atmospheric Administration)
- **Purpose:** Provides definitions for extreme storms.
- **URL:** [NOAA Storm Prediction Center](https://www.spc.noaa.gov/)

## Validation

### validate_risk_definition
- **Purpose:** Validates a risk definition dictionary.
- **Input:** A dictionary representing a risk definition.
- **Output:** `True` if valid, `False` otherwise.
- **Raises:** `ValueError` if the definition is invalid.

### get_consensus_thresholds
- **Purpose:** Returns consensus thresholds based on major governmental and insurance providers.
- **Output:** A dictionary of risk thresholds.
- **Raises:** `ValueError` if thresholds are invalid or inconsistent.

## Additional Definitions

### ClimateRiskAnalyzer
- **Purpose:** Analyzes various climate risks including extreme heat, flooding, wildfire, and extreme storms.
- **Location:** `multi_tool_agent/weather_risks.py`

### ADKAgentCoordinator
- **Purpose:** Coordinates agents using the Google Agent Development Kit (ADK).
- **Location:** `multi_tool_agent/adk_integration.py`

### AgentCapability
- **Purpose:** Represents the capabilities of an agent.
- **Location:** `multi_tool_agent/agent_team.py`

### AgentTeam
- **Purpose:** Represents a team of agents.
- **Location:** `multi_tool_agent/agent_team.py`

### AgentTeamManager
- **Purpose:** Manages a team of agents.
- **Location:** `multi_tool_agent/agent_team.py`

### AnalysisSession
- **Purpose:** Represents a session for climate risk analysis.
- **Location:** `multi_tool_agent/session_manager.py`

## Workflow Patterns

### SequentialWorkflow
- **Purpose:** Manages ordered execution of climate analysis tasks.
- **Fields:**
  - `name` (str): Name of the workflow.
  - `sub_agents` (List[Agent]): List of agents to execute in sequence.
  - `context` (Dict): Shared context between agents.
- **Location:** `multi_tool_agent/workflows.py`

### ParallelWorkflow
- **Purpose:** Manages concurrent execution of independent climate analysis tasks.
- **Fields:**
  - `name` (str): Name of the workflow.
  - `sub_agents` (List[Agent]): List of agents to execute in parallel.
  - `max_concurrent` (int): Maximum number of concurrent executions.
- **Location:** `multi_tool_agent/workflows.py`

### LoopWorkflow
- **Purpose:** Manages iterative climate analysis tasks.
- **Fields:**
  - `name` (str): Name of the workflow.
  - `sub_agents` (List[Agent]): List of agents to execute in loop.
  - `max_iterations` (int): Maximum number of iterations.
  - `termination_condition` (Callable): Function to check loop termination.
- **Location:** `multi_tool_agent/workflows.py`

## Communication Mechanisms

### SharedState
- **Purpose:** Manages shared state between agents.
- **Fields:**
  - `session_state` (Dict): Current session state.
  - `agent_states` (Dict[str, AgentState]): States of individual agents.
  - `context` (Dict): Shared context between agents.
- **Location:** `multi_tool_agent/communication.py`

### AgentTransfer
- **Purpose:** Manages transfer of control between agents.
- **Fields:**
  - `source_agent` (str): Name of the source agent.
  - `target_agent` (str): Name of the target agent.
  - `context` (Dict): Context to transfer.
  - `priority` (int): Transfer priority.
- **Location:** `multi_tool_agent/communication.py`

### ExplicitInvocation
- **Purpose:** Manages explicit agent invocations.
- **Fields:**
  - `agent_name` (str): Name of the agent to invoke.
  - `request` (Dict): Request parameters.
  - `context` (Dict): Invocation context.
  - `timeout` (int): Invocation timeout.
- **Location:** `multi_tool_agent/communication.py`

## Tool System

### ClimateTool
- **Purpose:** Base class for climate analysis tools.
- **Fields:**
  - `name` (str): Tool name.
  - `description` (str): Tool description.
  - `parameters` (Dict): Tool parameters.
  - `required_capabilities` (List[str]): Required agent capabilities.
- **Location:** `multi_tool_agent/tools.py`

### RiskAnalysisTool
- **Purpose:** Tool for climate risk analysis.
- **Fields:**
  - `risk_types` (List[str]): Types of risks to analyze.
  - `thresholds` (Dict): Risk thresholds.
  - `sources` (List[str]): Data sources.
- **Location:** `multi_tool_agent/tools.py`

### HistoricalAnalysisTool
- **Purpose:** Tool for historical climate analysis.
- **Fields:**
  - `time_range` (Tuple[datetime, datetime]): Analysis time range.
  - `metrics` (List[str]): Metrics to analyze.
  - `aggregation` (str): Data aggregation method.
- **Location:** `multi_tool_agent/tools.py`

### NewsMonitoringTool
- **Purpose:** Tool for climate news monitoring.
- **Fields:**
  - `sources` (List[str]): News sources to monitor.
  - `keywords` (List[str]): Keywords to track.
  - `update_frequency` (int): Update frequency in seconds.
- **Location:** `multi_tool_agent/tools.py`

## Error Handling

### ErrorRecovery
- **Purpose:** Manages error recovery for climate analysis.
- **Fields:**
  - `max_retries` (int): Maximum number of retry attempts.
  - `retry_delay` (int): Delay between retries in seconds.
  - `error_handlers` (Dict[str, Callable]): Error handlers for different error types.
- **Location:** `multi_tool_agent/error_handling.py`

### StateRecovery
- **Purpose:** Manages state recovery after errors.
- **Fields:**
  - `checkpoint_frequency` (int): Frequency of state checkpoints.
  - `recovery_strategy` (str): Strategy for state recovery.
  - `backup_location` (str): Location for state backups.
- **Location:** `multi_tool_agent/error_handling.py` 