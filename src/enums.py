"""
General enums for use across all src/ modules in Pythia.

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
    """Type of A2A message."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    OTHER = "other"

class PriorityLevel(Enum):
    """Priority of a message or task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
