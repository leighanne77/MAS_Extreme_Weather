"""
A2A Message Structure

Implements the A2A protocol message envelope and headers structure.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from .enums import MessageType, Priority, StatusCode


@dataclass
class A2AMessageHeaders:
    """A2A Message Headers"""
    content_type: str = "application/json"
    encoding: str = "utf-8"
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert headers to dictionary."""
        headers = asdict(self)
        if self.expires_at:
            headers['expires_at'] = self.expires_at.isoformat()
        return headers
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessageHeaders':
        """Create headers from dictionary."""
        if 'expires_at' in data and data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)


@dataclass
class A2AMessage:
    """A2A Message Envelope"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_type: MessageType = MessageType.REQUEST
    priority: Priority = Priority.NORMAL
    sender: str = ""
    recipients: List[str] = field(default_factory=list)
    content: Union[str, Dict[str, Any]] = ""
    headers: A2AMessageHeaders = field(default_factory=A2AMessageHeaders)
    status_code: Optional[StatusCode] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization validation."""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.message_type, str):
            self.message_type = MessageType(self.message_type)
        if isinstance(self.priority, int):
            self.priority = Priority(self.priority)
        if isinstance(self.status_code, int):
            self.status_code = StatusCode(self.status_code)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        message_dict = {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'sender': self.sender,
            'recipients': self.recipients,
            'content': self.content,
            'headers': self.headers.to_dict()
        }
        
        if self.status_code:
            message_dict['status_code'] = self.status_code.value
        if self.error_message:
            message_dict['error_message'] = self.error_message
            
        return message_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary."""
        headers_data = data.pop('headers', {})
        headers = A2AMessageHeaders.from_dict(headers_data)
        return cls(headers=headers, **data)
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if not self.headers.expires_at:
            return False
        return datetime.now(timezone.utc) > self.headers.expires_at
    
    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return self.headers.retry_count < self.headers.max_retries
    
    def increment_retry(self) -> None:
        """Increment retry count."""
        self.headers.retry_count += 1
    
    def add_custom_header(self, key: str, value: str) -> None:
        """Add custom header."""
        self.headers.custom_headers[key] = value
    
    def get_custom_header(self, key: str) -> Optional[str]:
        """Get custom header value."""
        return self.headers.custom_headers.get(key)
    
    def validate(self) -> List[str]:
        """Validate message structure."""
        errors = []
        
        if not self.sender:
            errors.append("Sender is required")
        
        if not self.recipients:
            errors.append("At least one recipient is required")
        
        if not self.content:
            errors.append("Content is required")
        
        if self.is_expired():
            errors.append("Message has expired")
        
        return errors


def create_request_message(
    sender: str,
    recipients: List[str],
    content: Union[str, Dict[str, Any]],
    message_type: MessageType = MessageType.REQUEST,
    priority: Priority = Priority.NORMAL,
    correlation_id: Optional[str] = None
) -> A2AMessage:
    """Create a request message."""
    headers = A2AMessageHeaders(
        correlation_id=correlation_id or str(uuid.uuid4()),
        expires_at=datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=30)
    )
    
    return A2AMessage(
        message_type=message_type,
        priority=priority,
        sender=sender,
        recipients=recipients,
        content=content,
        headers=headers
    )


def create_response_message(
    original_message: A2AMessage,
    content: Union[str, Dict[str, Any]],
    status_code: StatusCode = StatusCode.OK,
    error_message: Optional[str] = None
) -> A2AMessage:
    """Create a response message."""
    headers = A2AMessageHeaders(
        correlation_id=original_message.headers.correlation_id,
        reply_to=original_message.sender
    )
    
    return A2AMessage(
        message_type=MessageType.RESPONSE,
        priority=original_message.priority,
        sender=original_message.recipients[0] if original_message.recipients else "",
        recipients=[original_message.sender],
        content=content,
        headers=headers,
        status_code=status_code,
        error_message=error_message
    )


def create_error_message(
    original_message: A2AMessage,
    status_code: StatusCode,
    error_message: str
) -> A2AMessage:
    """Create an error message."""
    return create_response_message(
        original_message=original_message,
        content={"error": error_message},
        status_code=status_code,
        error_message=error_message
    ) 