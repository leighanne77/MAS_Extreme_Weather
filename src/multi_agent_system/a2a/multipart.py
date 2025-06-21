"""
A2A Multi-Part Messages

Implements multi-part message support for the A2A protocol.
"""

import uuid
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from .message import A2AMessage, A2AMessageHeaders
from .parts import A2APart
from .enums import MessageType, Priority, StatusCode


@dataclass
class A2AMultiPartMessage(A2AMessage):
    """A2A Multi-Part Message"""
    parts: List[A2APart] = field(default_factory=list)
    boundary: str = field(default_factory=lambda: f"boundary_{uuid.uuid4().hex}")
    
    def __post_init__(self):
        """Post-initialization setup."""
        super().__post_init__()
        
        # Update content type for multi-part messages
        if not self.headers.content_type.startswith('multipart/'):
            self.headers.content_type = f'multipart/mixed; boundary="{self.boundary}"'
    
    def add_part(self, part: A2APart) -> None:
        """Add a part to the message."""
        self.parts.append(part)
    
    def add_text_part(self, content: str, part_id: Optional[str] = None) -> A2APart:
        """Add a text part to the message."""
        from .parts import create_text_part
        part = create_text_part(content, part_id)
        self.add_part(part)
        return part
    
    def add_data_part(self, content: Dict[str, Any], part_id: Optional[str] = None) -> A2APart:
        """Add a data part to the message."""
        from .parts import create_data_part
        part = create_data_part(content, part_id)
        self.add_part(part)
        return part
    
    def add_file_part(self, file_path: str, part_id: Optional[str] = None) -> A2APart:
        """Add a file part to the message."""
        from .parts import create_file_part
        part = create_file_part(file_path, part_id)
        self.add_part(part)
        return part
    
    def add_binary_part(self, content: bytes, content_type: str = "application/octet-stream", part_id: Optional[str] = None) -> A2APart:
        """Add a binary part to the message."""
        from .parts import create_binary_part
        part = create_binary_part(content, content_type, part_id)
        self.add_part(part)
        return part
    
    def get_part(self, part_id: str) -> Optional[A2APart]:
        """Get a part by ID."""
        for part in self.parts:
            if part.id == part_id:
                return part
        return None
    
    def get_parts_by_type(self, part_type: str) -> List[A2APart]:
        """Get all parts of a specific type."""
        return [part for part in self.parts if part.part_type.value == part_type]
    
    def get_text_parts(self) -> List[A2APart]:
        """Get all text parts."""
        return self.get_parts_by_type('text')
    
    def get_data_parts(self) -> List[A2APart]:
        """Get all data parts."""
        return self.get_parts_by_type('data')
    
    def get_file_parts(self) -> List[A2APart]:
        """Get all file parts."""
        return self.get_parts_by_type('file')
    
    def remove_part(self, part_id: str) -> bool:
        """Remove a part by ID."""
        for i, part in enumerate(self.parts):
            if part.id == part_id:
                del self.parts[i]
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert multi-part message to dictionary."""
        message_dict = super().to_dict()
        message_dict['parts'] = [part.to_dict() for part in self.parts]
        message_dict['boundary'] = self.boundary
        return message_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMultiPartMessage':
        """Create multi-part message from dictionary."""
        parts_data = data.pop('parts', [])
        boundary = data.pop('boundary', f"boundary_{uuid.uuid4().hex}")
        
        # Create base message
        message = super().from_dict(data)
        
        # Create multi-part message
        multipart_message = cls(
            id=message.id,
            timestamp=message.timestamp,
            message_type=message.message_type,
            priority=message.priority,
            sender=message.sender,
            recipients=message.recipients,
            content=message.content,
            headers=message.headers,
            status_code=message.status_code,
            error_message=message.error_message,
            boundary=boundary
        )
        
        # Add parts
        for part_data in parts_data:
            part = A2APart.from_dict(part_data)
            multipart_message.add_part(part)
        
        return multipart_message
    
    def validate(self) -> List[str]:
        """Validate multi-part message structure."""
        errors = super().validate()
        
        # Validate parts
        for part in self.parts:
            part_errors = part.validate()
            errors.extend([f"Part {part.id}: {error}" for error in part_errors])
        
        # Check for duplicate part IDs
        part_ids = [part.id for part in self.parts]
        if len(part_ids) != len(set(part_ids)):
            errors.append("Duplicate part IDs found")
        
        return errors
    
    def get_total_size(self) -> int:
        """Get total size of all parts."""
        return sum(part.size or 0 for part in self.parts)
    
    def get_part_count(self) -> int:
        """Get number of parts in the message."""
        return len(self.parts)
    
    def has_parts(self) -> bool:
        """Check if message has any parts."""
        return len(self.parts) > 0
    
    def is_single_part(self) -> bool:
        """Check if message has exactly one part."""
        return len(self.parts) == 1
    
    def get_main_content(self) -> Optional[Union[str, Dict[str, Any]]]:
        """Get the main content (first text or data part)."""
        for part in self.parts:
            if part.part_type.value in ['text', 'data']:
                if part.part_type.value == 'text':
                    return part.get_content_as_text()
                else:
                    return part.get_content_as_dict()
        return None


def create_multipart_message(
    sender: str,
    recipients: List[str],
    parts: Optional[List[A2APart]] = None,
    message_type: MessageType = MessageType.REQUEST,
    priority: Priority = Priority.NORMAL
) -> A2AMultiPartMessage:
    """Create a multi-part message."""
    message = A2AMultiPartMessage(
        message_type=message_type,
        priority=priority,
        sender=sender,
        recipients=recipients,
        content="",  # Content will be in parts
        headers=A2AMessageHeaders()
    )
    
    if parts:
        for part in parts:
            message.add_part(part)
    
    return message


def create_multipart_response(
    original_message: A2AMultiPartMessage,
    parts: List[A2APart],
    status_code: StatusCode = StatusCode.OK
) -> A2AMultiPartMessage:
    """Create a multi-part response message."""
    response = A2AMultiPartMessage(
        message_type=MessageType.RESPONSE,
        priority=original_message.priority,
        sender=original_message.recipients[0] if original_message.recipients else "",
        recipients=[original_message.sender],
        content="",
        headers=A2AMessageHeaders(
            correlation_id=original_message.headers.correlation_id,
            reply_to=original_message.sender
        ),
        status_code=status_code
    )
    
    for part in parts:
        response.add_part(part)
    
    return response 