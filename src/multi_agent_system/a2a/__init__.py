"""
A2A (Agent-to-Agent) Protocol Implementation

This package provides a complete implementation of the A2A protocol
for multi-agent communication, including message structure, part types,
artifact management, and task management.
"""

from .artifact_manager import A2AArtifactManager, artifact_manager
from .artifacts import (
    A2AArtifact,
    ArtifactMetadata,
    ArtifactPriority,
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
    create_artifact,
    create_recommendation_artifact,
    create_report_artifact,
    create_visualization_artifact,
)
from .enums import MessageType, PartType, StatusCode
from .message import (
    A2AMessage,
    A2AMessageHeaders,
    A2AMessagePart,
    create_data_message,
    create_error_message,
    create_multipart_message,
    create_request_message,
    create_response_message,
    create_text_message,
)
from .multipart import A2AMultiPartMessage
from .parts import (
    A2APart,
    create_binary_part,
    create_data_part,
    create_file_part,
    create_text_part,
)
from .router import A2AMessageRouter
from .task_manager import TaskManager, task_manager

__all__ = [
    # Enums
    'StatusCode', 'MessageType', 'PartType',

    # Messages
    'A2AMessage', 'A2AMessageHeaders', 'A2AMessagePart', 'A2AMultiPartMessage',
    'create_request_message', 'create_response_message', 'create_error_message',
    'create_text_message', 'create_data_message', 'create_multipart_message',

    # Parts
    'A2APart', 'create_text_part', 'create_data_part', 'create_file_part', 'create_binary_part',

    # Router
    'A2AMessageRouter',

    # Artifacts
    'A2AArtifact', 'ArtifactType', 'ArtifactStatus', 'ArtifactPriority',
    'ArtifactMetadata', 'ArtifactVersion',
    'create_artifact', 'create_report_artifact', 'create_recommendation_artifact',
    'create_visualization_artifact',

    # Managers
    'A2AArtifactManager', 'artifact_manager',
    'TaskManager', 'task_manager'
]
