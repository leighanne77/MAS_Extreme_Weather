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
class ADKClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize ADK client.
        
        Args:
            base_url: ADK service base URL
            api_key: Authentication key
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
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
class CommunicationManager:
    def __init__(self, session: AnalysisSession):
        """Initialize communication manager.
        
        Args:
            session: Current analysis session
        """
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
from multi_tool_agent.adk_integration import ADKClient

client = ADKClient(
    base_url="https://adk-service.example.com",
    api_key="your-api-key"
)

response = await client.request(
    endpoint="analyze",
    data={"location": "New York"}
)
```

### Agent Communication
```python
from multi_tool_agent.communication import CommunicationManager

comm_manager = CommunicationManager(session)
await comm_manager.send_message(
    source="risk_analyzer",
    target="validation_agent",
    message={"type": "data", "content": analysis_result}
)
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