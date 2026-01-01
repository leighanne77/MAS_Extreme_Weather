"""
Enums for data loader status, provenance, and type.
"""
from enum import Enum

class DataLoadStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"

class ProvenanceType(Enum):
    API = "api"
    MCP = "mcp"
    STATIC = "static"
    MANUAL = "manual"

class DataSourceType(Enum):
    AGRICULTURE = "agriculture"
    WATER = "water"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"

class ErrorType(Enum):
    NETWORK = "network"
    PARSING = "parsing"
    VALIDATION = "validation"
    PERMISSION = "permission"
    UNKNOWN = "unknown"

class UpdateFrequency(Enum):
    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    MANUAL = "manual"

class DataFormat(Enum):
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"
    OTHER = "other"

class AccessLevel(Enum):
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    INTERNAL = "internal"

class ArtifactType(Enum):
    DATASET = "dataset"
    MODEL = "model"
    REPORT = "report"
    VISUALIZATION = "visualization"
    LOG = "log"
