"""
General enums for use across all src/ modules in MAS.

Naming conventions:
- Prefix with domain if needed for clarity (e.g., DataLoadStatus, AgentRole, ArtifactType).
- Use clear, descriptive names and docstrings for each enum and value.

See documentation in docs/Definitions.md for usage examples and integration guidance.
"""
from enum import Enum

class DataLoadStatus(Enum):
    """Status of a data loader or agent operation."""
    SUCCESS = "success"
    ERROR = "error"

class DataProvenance(Enum):
    """Origin of the data used or produced."""
    API = "api"
    MCP = "mcp"
    STATIC = "static"
    MANUAL = "manual"

class DataDomain(Enum):
    """Domain/type of the data source."""
    AGRICULTURE = "agriculture"
    WATER = "water"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"

class DataErrorType(Enum):
    """Type of error encountered during data operations."""
    NETWORK = "network"
    PARSING = "parsing"
    VALIDATION = "validation"
    PERMISSION = "permission"
    UNKNOWN = "unknown"

class DataUpdateFrequency(Enum):
    """How often the data is updated or refreshed."""
    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    MANUAL = "manual"

class DataFormat(Enum):
    """Format of the data returned or processed."""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"
    OTHER = "other"

class DataAccessLevel(Enum):
    """Access permissions for the data."""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    INTERNAL = "internal"

class ArtifactType(Enum):
    """Type of artifact produced by agents or loaders."""
    DATASET = "dataset"
    MODEL = "model"
    REPORT = "report"
    VISUALIZATION = "visualization"
    LOG = "log"

# System/Agent/Observability enums
class ErrorSeverity(Enum):
    """Severity of an error for logging and recovery."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentRole(Enum):
    """Role of an agent in the system."""
    ANALYST = "analyst"
    VALIDATOR = "validator"
    INGESTOR = "ingestor"
    REPORTER = "reporter"
    ADMIN = "admin"

class InteractionType(Enum):
    """Pattern of agent interaction."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BRANCHING = "branching"
    RECURSIVE = "recursive"

class DecisionPattern(Enum):
    """Pattern of agent decision-making."""
    LINEAR = "linear"
    BRANCHING = "branching"
    BACKTRACKING = "backtracking"
    OPTIMIZATION = "optimization"

class MessageType(Enum):
    """Type of A2A message.
    
    Note: This is the canonical MessageType enum. The A2A module
    (multi_agent_system/a2a/enums.py) re-exports this for backward compatibility.
    """
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_COMPLETION = "task_completion"
    ARTIFACT_CREATED = "artifact_created"
    ARTIFACT_REQUESTED = "artifact_requested"
    OTHER = "other"

class PriorityLevel(Enum):
    """Priority of a message or task (string values).
    
    For numeric priority values, see multi_agent_system/a2a/enums.Priority.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Communication status constants - use instead of string literals
class CommunicationStatus(Enum):
    """Status values for agent communication responses."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


# =============================================================================
# A2A Protocol Enums
# =============================================================================
# These enums are used by the A2A (Agent-to-Agent) protocol implementation.
# The A2A module (multi_agent_system/a2a/enums.py) re-exports these for
# backward compatibility.

class Priority(Enum):
    """A2A Message Priority Levels (numeric for sorting/comparison).
    
    Use these for A2A protocol messages where numeric priority is needed.
    For general-purpose string priorities, see PriorityLevel.
    """
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class StatusCode(Enum):
    """A2A Protocol Status Codes.
    
    HTTP-style status codes plus A2A-specific codes for agent communication.
    """
    # Success codes
    OK = 200
    CREATED = 201
    ACCEPTED = 202

    # Client error codes
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409

    # Server error codes
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503

    # A2A specific codes
    AGENT_NOT_FOUND = 1001
    MESSAGE_FORMAT_ERROR = 1002
    ROUTING_ERROR = 1003
    TASK_NOT_FOUND = 1004
    ARTIFACT_NOT_FOUND = 1005


class PartType(Enum):
    """A2A Message Part Types for multipart messages."""
    TEXT = "text"
    DATA = "data"
    FILE = "file"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    BINARY = "binary"


# Status code descriptions for human-readable messages
STATUS_DESCRIPTIONS: dict[StatusCode, str] = {
    StatusCode.OK: "Request completed successfully",
    StatusCode.CREATED: "Resource created successfully",
    StatusCode.ACCEPTED: "Request accepted for processing",
    StatusCode.BAD_REQUEST: "Invalid request format or parameters",
    StatusCode.UNAUTHORIZED: "Authentication required",
    StatusCode.FORBIDDEN: "Access denied",
    StatusCode.NOT_FOUND: "Resource not found",
    StatusCode.CONFLICT: "Resource conflict",
    StatusCode.INTERNAL_ERROR: "Internal server error",
    StatusCode.NOT_IMPLEMENTED: "Feature not implemented",
    StatusCode.SERVICE_UNAVAILABLE: "Service temporarily unavailable",
    StatusCode.AGENT_NOT_FOUND: "Target agent not found",
    StatusCode.MESSAGE_FORMAT_ERROR: "Invalid message format",
    StatusCode.ROUTING_ERROR: "Message routing failed",
    StatusCode.TASK_NOT_FOUND: "Task not found",
    StatusCode.ARTIFACT_NOT_FOUND: "Artifact not found",
}


def get_status_description(status_code: StatusCode) -> str:
    """Get human-readable description for a status code."""
    return STATUS_DESCRIPTIONS.get(status_code, "Unknown status code")
