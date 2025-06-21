"""
A2A (Agent-to-Agent) Protocol Implementation

This package provides a complete implementation of the A2A protocol
for multi-agent communication, including message structure, part types,
artifact management, and task management.
"""

from .enums import StatusCode, MessageType, PartType
from .message import A2AMessage, A2AMessageHeaders, create_request_message, create_response_message, create_error_message
from .multipart import A2AMultiPartMessage
from .parts import A2APart, create_text_part, create_data_part, create_file_part, create_binary_part
from .router import A2AMessageRouter
from .artifacts import (
    A2AArtifact, ArtifactType, ArtifactStatus, ArtifactPriority,
    ArtifactMetadata, ArtifactVersion,
    create_artifact, create_report_artifact, create_recommendation_artifact,
    create_visualization_artifact
)
from .artifact_manager import A2AArtifactManager, artifact_manager
from .task_manager import A2ATaskManager, task_manager

__all__ = [
    # Enums
    'StatusCode', 'MessageType', 'PartType',
    
    # Messages
    'A2AMessage', 'A2AMessageHeaders', 'A2AMultiPartMessage',
    'create_request_message', 'create_response_message', 'create_error_message',
    
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
    'A2ATaskManager', 'task_manager'
] 