# API Documentation

## Overview
This document provides comprehensive documentation for all APIs in the Multi-Agent Climate Risk Analysis System. It covers FastAPI endpoints, ADK service integration, agent communication interfaces, session management, and artifact management.

## FastAPI Endpoints

### Health Check
```http
GET /health
```
Checks the health status of the system.

**Response:**
```json
{
    "status": "healthy"
}
```

### Climate Risk Analysis
```http
POST /analyze
```
Analyzes climate risks for a given location.

**Request Body:**
```json
{
    "location": "string"  // Address or location identifier
}
```

**Response:**
```json
{
    "risk_level": "string",  // LOW, MEDIUM, HIGH, EXTREME
    "confidence": "float",   // 0.0 to 1.0
    "factors": [
        {
            "type": "string",
            "severity": "string",
            "description": "string"
        }
    ],
    "recommendations": [
        "string"
    ]
}
```

### Session Management
```http
GET /sessions/{session_id}
```
Retrieves information about a specific session.

**Path Parameters:**
- `session_id`: Unique session identifier

**Response:**
```json
{
    "id": "string",
    "created_at": "datetime",
    "status": "string",
    "state": {
        "key": "value"
    }
}
```

### Artifact Management
```http
GET /sessions/{session_id}/artifacts
```
Retrieves artifacts for a specific session.

**Path Parameters:**
- `session_id`: Unique session identifier

**Query Parameters:**
- `agent_id` (optional): Filter by agent
- `artifact_type` (optional): Filter by type

**Response:**
```json
[
    {
        "id": "string",
        "type": "string",
        "agent_id": "string",
        "created_at": "datetime",
        "data": {
            "key": "value"
        }
    }
]
```

## ADK Service Integration

### ADKClient
```python
from src.multi_agent_system.adk_integration import ADKClient

class ADKClient:
    def __init__(
        self,
        project_id: str,
        location: str,
        model: str = "gemini-2.0-flash"
    ):
        self.project_id = project_id
        self.location = location
        self.model = model
        self.client = aiplatform.gapic.PredictionServiceClient(
            client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        )

    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 1024
    ) -> str:
        # Implementation details...
        pass
```

### Methods

#### Request
```python
async def request(
    self,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    method: str = "POST"
) -> ADKResponse:
    """Make request to ADK service.
    
    Args:
        endpoint: Service endpoint
        data: Request data
        method: HTTP method
        
    Returns:
        ADKResponse object
    """
```

#### Close
```python
async def close(self) -> None:
    """Close ADK client session."""
```

## Agent Communication Interfaces

### CommunicationManager
```python
from src.multi_agent_system.communication import CommunicationManager

class CommunicationManager:
    def __init__(self, session: AnalysisSession):
        self.session = session
        self.shared_state = SharedState()

    async def broadcast_message(
        self,
        message: str,
        sender_id: str
    ) -> None:
        # Implementation details...
        pass
```

### Methods

#### Send Message
```python
async def send_message(
    self,
    source: str,
    target: str,
    message: Dict[str, Any]
) -> None:
    """Send message between agents.
    
    Args:
        source: Source agent ID
        target: Target agent ID
        message: Message content
    """
```

#### Get Shared State
```python
def get_shared_state(self) -> SharedState:
    """Get current shared state.
    
    Returns:
        SharedState object
    """
```

## Session Management API

### SessionManager
```python
class SessionManager:
    def __init__(
        self,
        session_timeout: timedelta = DEFAULT_SESSION_TIMEOUT,
        storage_dir: str = SESSION_STORAGE_DIR,
        max_concurrent: int = MAX_CONCURRENT_OPERATIONS
    ):
        """Initialize session manager.
        
        Args:
            session_timeout: Maximum session age
            storage_dir: Session storage directory
            max_concurrent: Maximum concurrent operations
        """
```

### Methods

#### Start
```python
async def start(self) -> None:
    """Start session manager and load persisted sessions."""
```

#### Stop
```python
async def stop(self) -> None:
    """Stop session manager and persist sessions."""
```

## Artifact Management API

### ArtifactManager
```python
class ArtifactManager:
    def __init__(self, base_dir: str = ARTIFACT_BASE_DIR):
        """Initialize artifact manager.
        
        Args:
            base_dir: Base directory for artifacts
        """
```

### Methods

#### Store Artifact
```python
async def store_artifact(
    self,
    session_id: str,
    agent_id: str,
    artifact_type: str,
    data: Dict[str, Any]
) -> str:
    """Store new artifact.
    
    Args:
        session_id: Session identifier
        agent_id: Agent identifier
        artifact_type: Type of artifact
        data: Artifact data
        
    Returns:
        Artifact ID
    """
```

#### List Artifacts
```python
async def list_artifacts(
    self,
    session_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    artifact_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List artifacts matching criteria.
    
    Args:
        session_id: Filter by session
        agent_id: Filter by agent
        artifact_type: Filter by type
        
    Returns:
        List of matching artifacts
    """
```

## Error Handling

### HTTP Status Codes
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

### Error Response Format
```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": {
            "key": "value"
        }
    }
}
```

## Rate Limiting

### Limits
- 100 requests per minute per API key
- 1000 requests per hour per API key

### Headers
- `X-RateLimit-Limit`: Maximum requests per period
- `X-RateLimit-Remaining`: Remaining requests in period
- `X-RateLimit-Reset`: Time until limit reset

## Authentication

### API Key Authentication
```http
Authorization: Bearer your-api-key
```

### Required Headers
```http
Content-Type: application/json
Accept: application/json
```

## Best Practices

### Request Handling
1. Always include error handling
2. Use appropriate HTTP methods
3. Validate request data
4. Handle rate limits
5. Implement retry logic

### Response Handling
1. Check status codes
2. Parse error responses
3. Handle timeouts
4. Validate response data
5. Implement fallback logic

### Security
1. Use HTTPS
2. Validate API keys
3. Sanitize input data
4. Implement rate limiting
5. Log security events

## Examples

### Basic Analysis Request
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"location": "New York"}
)
result = response.json()
```

### ADK Service Integration
```python
from src.multi_agent_system.adk_integration import ADKClient

client = ADKClient(
    project_id="your-project-id",
    location="us-central1"
)
response = await client.generate_content("Analyze climate risks for New York")
```

### Agent Communication
```python
from src.multi_agent_system.communication import CommunicationManager

comm_manager = CommunicationManager(session)
await comm_manager.broadcast_message("Task completed", "agent_1")
```

## Versioning

### API Version
Current version: 1.0.0

### Version Header
```http
X-API-Version: 1.0.0
```

## Support

### Contact
- Email: support@example.com
- Documentation: https://docs.example.com
- Status: https://status.example.com

### Response Times
- Critical issues: < 1 hour
- High priority: < 4 hours
- Normal priority: < 24 hours
- Low priority: < 72 hours 

# API Reference

> **Note:** All code imports should use the `src.multi_agent_system` package path due to the src/ layout.

## Example Import
```python
from src.multi_agent_system.agent_team import AgentTeam
from src.multi_agent_system.enhanced_coordinator import EnhancedADKCoordinator
```

## Modules
- [agent_team](#agent_team)
- [agent_tools](#agent_tools)
- [enhanced_coordinator](#enhanced_coordinator)
- [communication](#communication)
- [artifact_manager](#artifact_manager)
- [workflows](#workflows)
- [adk_integration](#adk_integration)
- [session_manager](#session_manager)
- [risk_definitions](#risk_definitions)
- [weather_risks](#weather_risks)
- [observability](#observability)

## agent_team
```python
from src.multi_agent_system.agent_team import AgentTeam, Agent
```
- **AgentTeam**: Manages a team of agents for coordinated risk analysis.
- **Agent**: Base class for specialized agents.

## agent_tools

from src.multi_agent_system.agent_tools import (
    get_cached_result,
    update_cache,
    handle_tool_error,
    execute_with_concurrency_limit,
    concurrency_limit
)

- **get_cached_result**: Retrieves cached results for a function call.
- **update_cache**: Updates the cache with new function call results.
- **handle_tool_error**: Handles errors during function execution.
- **execute_with_concurrency_limit**: Executes a function with a concurrency limit.
- **concurrency_limit**: Limits the number of concurrent function executions.

## enhanced_coordinator
```python
from src.multi_agent_system.enhanced_coordinator import EnhancedADKCoordinator
```
- **EnhancedADKCoordinator**: Orchestrates parallel agent execution and state management.

## communication
```python
from src.multi_agent_system.communication import CommunicationManager, SharedState
```
- **CommunicationManager**: Handles inter-agent communication.
- **SharedState**: Manages shared state between agents.

## artifact_manager
```python
from src.multi_agent_system.artifact_manager import ArtifactManager
```
- **ArtifactManager**: Manages storage and retrieval of agent outputs.

## workflows
```python
from src.multi_agent_system.workflows import WorkflowManager, WorkflowStep
```
- **WorkflowManager**: Orchestrates multi-step workflows.
- **WorkflowStep**: Represents a step in a workflow.

## adk_integration
```python
from src.multi_agent_system.adk_integration import ADKAgentCoordinator
```
- **ADKAgentCoordinator**: Integrates with the ADK system for agent execution.

## session_manager
```python
from src.multi_agent_system.session_manager import SessionManager, AnalysisSession
```
- **SessionManager**: Manages user sessions and agent state.
- **AnalysisSession**: Represents a session for risk analysis.

## risk_definitions
```python
from src.multi_agent_system.risk_definitions import RiskType, RiskLevel, RiskDefinition
```
- **RiskType**: Enum for risk types.
- **RiskLevel**: Enum for risk severity levels.
- **RiskDefinition**: Defines thresholds and sources for risks.

## weather_risks
```python
from src.multi_agent_system.weather_risks import ClimateRiskAnalyzer
```
- **ClimateRiskAnalyzer**: Analyzes climate risks using real-time and historical data.

## observability
```python
from src.multi_agent_system.observability import ObservabilityManager
```
- **ObservabilityManager**: Manages system observability and monitoring.

## Observability System

### ObservabilityManager

The `ObservabilityManager` provides a high-level interface for system observability and monitoring. It wraps the internal `PatternMonitor` implementation and ensures robust state management and error recovery.

### Key Features

- **Durable State Management**: All checkpoints are persisted to disk, ensuring state is not lost even in case of system failures.
- **Granular Recovery Points**: Checkpoints can be created at specific points in execution, allowing for precise state recovery.
- **Concurrent Operation Support**: Thread-safe checkpoint operations with async/await support.
- **Automatic Cleanup**: Built-in mechanisms for managing checkpoint lifecycle and storage.

### Key Methods

- **create_checkpoint(agent_id, state, context, tool_calls, recovery_point, metadata)**: Creates a durable system checkpoint for the specified agent. Ensures agent patterns are initialized before creating the checkpoint.
- **restore_checkpoint(checkpoint_id)**: Restores a checkpoint by its ID, with full state recovery.
- **list_checkpoints(agent_id)**: Lists available checkpoints, optionally filtered by agent_id.
- **delete_checkpoint(checkpoint_id)**: Deletes a specific checkpoint.
- **cleanup_old_checkpoints(max_age_days)**: Removes checkpoints older than specified age.
- **track_error(agent_id, error_type, severity, tool_name, context, stack_trace)**: Tracks an error for the specified agent. Ensures agent patterns are initialized.
- **track_interaction(agent_id, interaction_type, start_time, end_time, success, token_usage, context_size, compressed_size, error_type, retry_count)**: Tracks an interaction for the specified agent. Ensures agent patterns are initialized.
- **track_decision(agent_id, pattern, start_time, end_time, branches, max_depth, success_rate, error_rate, optimization_score)**: Tracks a decision for the specified agent. Ensures agent patterns are initialized.
- **get_agent_patterns(agent_id)**: Returns the patterns for the specified agent. Ensures agent patterns are initialized.
- **get_interaction_patterns()**: Returns the interaction patterns.
- **get_decision_patterns()**: Returns the decision patterns.
- **get_error_patterns()**: Returns the error patterns.
- **get_retry_patterns()**: Returns the retry patterns.
- **get_token_usage_patterns()**: Returns the token usage patterns.
- **get_context_patterns()**: Returns the context patterns.
- **analyze_patterns()**: Analyzes the patterns and returns insights.

### Example Usage

```python
# Initialize observability manager
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

# Restore from checkpoint
checkpoint = await manager.restore_checkpoint(checkpoint_id)
if checkpoint:
    # Resume execution from checkpoint
    resume_execution(checkpoint.state, checkpoint.context)

# Clean up old checkpoints
deleted = await manager.cleanup_old_checkpoints(max_age_days=7)
print(f"Cleaned up {deleted} old checkpoints")
```

## PatternMonitor

The `PatternMonitor` is the internal implementation for monitoring patterns. It ensures that agent patterns are initialized before any operation and provides robust state persistence.

### Key Features

- **Durable Storage**: All checkpoints are stored on disk with proper serialization.
- **Concurrent Safety**: Thread-safe operations with async/await support.
- **Granular State Management**: Support for specific recovery points and metadata.
- **Automatic Cleanup**: Built-in mechanisms for managing checkpoint lifecycle.

### Key Methods

- **create_checkpoint(agent_id, state, context, tool_calls, recovery_point, metadata)**: Creates a durable system checkpoint for the specified agent. Ensures agent patterns are initialized.
- **restore_checkpoint(checkpoint_id)**: Restores a checkpoint by its ID, with full state recovery.
- **list_checkpoints(agent_id)**: Lists available checkpoints, optionally filtered by agent_id.
- **delete_checkpoint(checkpoint_id)**: Deletes a specific checkpoint.
- **cleanup_old_checkpoints(max_age_days)**: Removes checkpoints older than specified age.
- **track_error(agent_id, error_type, severity, tool_name, context, stack_trace)**: Tracks an error for the specified agent. Ensures agent patterns are initialized.
- **track_interaction(agent_id, interaction_type, start_time, end_time, success, token_usage, context_size, compressed_size, error_type, retry_count)**: Tracks an interaction for the specified agent. Ensures agent patterns are initialized.
- **track_decision(agent_id, pattern, start_time, end_time, branches, max_depth, success_rate, error_rate, optimization_score)**: Tracks a decision for the specified agent. Ensures agent patterns are initialized.
- **get_agent_patterns(agent_id)**: Returns the patterns for the specified agent. Ensures agent patterns are initialized.
- **get_interaction_patterns()**: Returns the interaction patterns.
- **get_decision_patterns()**: Returns the decision patterns.
- **get_error_patterns()**: Returns the error patterns.
- **get_retry_patterns()**: Returns the retry patterns.
- **get_token_usage_patterns()**: Returns the token usage patterns.
- **get_context_patterns()**: Returns the context patterns.
- **analyze_patterns()**: Analyzes the patterns and returns insights.

### Example Usage

```python
# Initialize pattern monitor
monitor = PatternMonitor(checkpoint_dir="checkpoints")

# Create a checkpoint with recovery point
checkpoint_id = await monitor.create_checkpoint(
    agent_id="risk_analyzer",
    state={"status": "running"},
    context={"location": "New York"},
    tool_calls=[{"tool": "analyze_risks"}],
    recovery_point="pre_risk_analysis",
    metadata={"analysis_type": "comprehensive"}
)

# List available checkpoints
checkpoints = await monitor.list_checkpoints(agent_id="risk_analyzer")
for checkpoint in checkpoints:
    print(f"Checkpoint {checkpoint['id']} at {checkpoint['timestamp']}")

# Restore from checkpoint
checkpoint = await monitor.restore_checkpoint(checkpoint_id)
if checkpoint:
    # Resume execution from checkpoint
    resume_execution(checkpoint.state, checkpoint.context)

# Clean up old checkpoints
deleted = await monitor.cleanup_old_checkpoints(max_age_days=7)
print(f"Cleaned up {deleted} old checkpoints")
```

## Data Classes

### Checkpoint

Represents a system checkpoint with enhanced persistence capabilities.

```python
@dataclass
class Checkpoint:
    id: str                    # Unique identifier
    agent_id: str             # ID of the agent
    timestamp: datetime       # When the checkpoint was created
    state: Dict[str, Any]     # Current agent state
    context: Dict[str, Any]   # Current context
    tool_calls: List[Dict[str, Any]]  # Recent tool calls
    recovery_point: str       # Identifies the specific point in execution
    metadata: Dict[str, Any]  # Additional metadata for recovery
```

### InteractionMetrics

Tracks metrics for agent interactions.

```python
@dataclass
class InteractionMetrics:
    agent_id: str             # ID of the agent
    interaction_type: InteractionType  # Type of interaction
    start_time: datetime      # When the interaction started
    end_time: datetime        # When the interaction ended
    success: bool             # Whether the interaction succeeded
    token_usage: Dict[str, int]  # Token usage statistics
    context_size: int         # Size of the context
    compressed_size: int      # Size of the compressed context
    error_type: Optional[str] # Type of error if any
    retry_count: int          # Number of retry attempts
```

### DecisionMetrics

Tracks metrics for agent decisions.

```python
@dataclass
class DecisionMetrics:
    agent_id: str             # ID of the agent
    pattern: DecisionPattern  # Decision pattern used
    start_time: datetime      # When the decision started
    end_time: datetime        # When the decision ended
    branches: int             # Number of decision branches
    max_depth: int            # Maximum decision depth
    success_rate: float       # Success rate of the decision
    error_rate: float         # Error rate of the decision
    optimization_score: float # Optimization score
```

### ErrorContext

Tracks error information.

```python
@dataclass
class ErrorContext:
    agent_id: str             # ID of the agent
    error_type: str           # Type of error
    severity: ErrorSeverity   # Error severity
    tool_name: str            # Name of the tool that caused the error
    context: Dict[str, Any]   # Error context
    stack_trace: str          # Stack trace of the error
```

## Enums

### InteractionType

Types of agent interactions.

```python
class InteractionType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"
```

### DecisionPattern

Types of decision patterns.

```python
class DecisionPattern(Enum):
    LINEAR = "linear"
    BRANCHING = "branching"
    RECURSIVE = "recursive"
    ADAPTIVE = "adaptive"
```

### ErrorSeverity

Levels of error severity.

```python
class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

## Function-Based Tools

The ADK framework automatically wraps regular Python functions as tools when they are added to an agent's tools list. This approach provides flexibility and quick integration.

### Tool Definition

Functions should be defined with clear parameter types and return values:

```python
def analyze_climate_risk(location: str, time_period: str) -> dict:
    """
    Analyzes climate risks for a specified location and time period.
    
    Args:
        location (str): The location to analyze
        time_period (str): The time period for analysis
        
    Returns:
        dict: Analysis results including risk levels and recommendations
    """
    # Implementation
    return {
        "status": "success",
        "risk_level": "high",
        "recommendations": ["action1", "action2"]
    }
```

### Adding Tools to Agents

```python
from multi_agent_system.adk_integration import ADKClient

# Create agent with function-based tools
climate_agent = ADKClient(
    model="gemini-pro",
    name="Climate Analyst",
    instruction="Analyze climate risks and provide recommendations",
    description="Expert in climate risk analysis",
    tools=[analyze_climate_risk, get_weather_data]  # Functions are automatically wrapped as tools
)
```

### Tool Parameters

- Use standard JSON-serializable types (string, integer, list, dictionary)
- Avoid default values for parameters
- Include clear type hints
- Document parameter requirements in docstrings

### Tool Return Values

- Return dictionaries with a "status" key
- Include relevant data in the response
- Handle errors gracefully
- Use consistent return formats

## Example Tools

### Climate Risk Analysis

```python
def analyze_climate_risk(location: str, time_period: str) -> dict:
    """
    Analyzes climate risks for a specified location and time period.
    
    Args:
        location (str): The location to analyze
        time_period (str): The time period for analysis
        
    Returns:
        dict: Analysis results including risk levels and recommendations
    """
    try:
        # Implementation
        return {
            "status": "success",
            "risk_level": "high",
            "recommendations": ["action1", "action2"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### Weather Data Retrieval

```python
def get_weather_data(location: str) -> dict:
    """
    Retrieves weather data for a specified location.
    
    Args:
        location (str): The location to get weather data for
        
    Returns:
        dict: Weather data including temperature and precipitation
    """
    try:
        # Implementation
        return {
            "status": "success",
            "temperature": 25.5,
            "precipitation": 0.2
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

## Best Practices

1. **Function Design**
   - Keep functions focused and single-purpose
   - Use clear, descriptive names
   - Include comprehensive docstrings
   - Implement proper error handling

2. **Parameter Handling**
   - Validate input parameters
   - Use type hints
   - Document parameter requirements
   - Avoid default values

3. **Return Values**
   - Use consistent return formats
   - Include status information
   - Handle errors gracefully
   - Document return types

4. **Error Handling**
   - Catch and handle exceptions
   - Return meaningful error messages
   - Log errors appropriately
   - Maintain system stability

5. **Testing**
   - Write unit tests for each function
   - Test error cases
   - Verify return formats
   - Check parameter validation 