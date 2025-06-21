"""
A2A Protocol Enums

Defines enumerations for message types, priority levels, and status codes
used in the A2A protocol implementation.
"""

from enum import Enum, auto
from typing import Dict, Any


class MessageType(Enum):
    """A2A Message Types"""
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


class Priority(Enum):
    """Message Priority Levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class StatusCode(Enum):
    """A2A Status Codes"""
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
    """A2A Part Types"""
    TEXT = "text"
    DATA = "data"
    FILE = "file"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    BINARY = "binary"


# Status code descriptions
STATUS_DESCRIPTIONS: Dict[StatusCode, str] = {
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
    StatusCode.ARTIFACT_NOT_FOUND: "Artifact not found"
}


def get_status_description(status_code: StatusCode) -> str:
    """Get description for a status code."""
    return STATUS_DESCRIPTIONS.get(status_code, "Unknown status code") 