"""
A2A Message Structure - Aligned with A2A Protocol Specifications

Implements the A2A protocol message structure following the specifications
from A2A_integration.md and A2A_reference.md, with proper part handling
and agent card compliance.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

# Handle both relative and absolute imports
try:
    from .enums import MessageType, PartType, Priority, StatusCode
except ImportError:
    from enums import MessageType, PartType, Priority, StatusCode


@dataclass
class A2AMessageHeaders:
    """A2A Message Headers following protocol specifications"""
    content_type: str = "application/json"
    encoding: str = "utf-8"
    correlation_id: str | None = None
    reply_to: str | None = None
    expires_at: datetime | None = None
    retry_count: int = 0
    max_retries: int = 3
    custom_headers: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert headers to dictionary following A2A protocol."""
        headers = asdict(self)
        if self.expires_at:
            headers['expires_at'] = self.expires_at.isoformat()
        return headers

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'A2AMessageHeaders':
        """Create headers from dictionary with proper validation."""
        if 'expires_at' in data and data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)


@dataclass
class A2AMessagePart:
    """A2A Message Part following protocol specifications"""
    kind: PartType
    text: str | None = None
    data: dict[str, Any] | None = None
    file: dict[str, Any] | None = None
    part_id: str | None = None

    def __post_init__(self):
        """Post-initialization validation and setup."""
        if isinstance(self.kind, str):
            self.kind = PartType(self.kind)
        if not self.part_id:
            self.part_id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        """Convert part to dictionary following A2A protocol."""
        part_dict = {
            "kind": self.kind.value,
            "partId": self.part_id
        }

        if self.text is not None:
            part_dict["text"] = self.text
        if self.data is not None:
            part_dict["data"] = self.data
        if self.file is not None:
            part_dict["file"] = self.file

        return part_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'A2AMessagePart':
        """Create part from dictionary with proper validation."""
        kind = PartType(data["kind"])
        part_id = data.get("partId")

        # Extract content based on kind
        text = data.get("text") if kind == PartType.TEXT else None
        data_content = data.get("data") if kind == PartType.DATA else None
        file_content = data.get("file") if kind == PartType.FILE else None

        return cls(
            kind=kind,
            text=text,
            data=data_content,
            file=file_content,
            part_id=part_id
        )

    def validate(self) -> list[str]:
        """Validate part structure following A2A protocol."""
        errors = []

        if not self.kind:
            errors.append("Part kind is required")

        # Validate content based on kind
        if self.kind == PartType.TEXT and not self.text:
            errors.append("Text content required for text part")
        elif self.kind == PartType.DATA and not self.data:
            errors.append("Data content required for data part")
        elif self.kind == PartType.FILE and not self.file:
            errors.append("File content required for file part")

        return errors


@dataclass
class A2AMessage:
    """A2A Message Envelope following protocol specifications"""
    role: str
    parts: list[A2AMessagePart]
    message_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    message_type: MessageType = MessageType.REQUEST
    priority: Priority = Priority.NORMAL
    sender: str = ""
    recipients: list[str] = field(default_factory=list)
    headers: A2AMessageHeaders = field(default_factory=A2AMessageHeaders)
    status_code: StatusCode | None = None
    error_message: str | None = None

    def __post_init__(self):
        """Post-initialization validation and setup."""
        if not self.message_id:
            self.message_id = str(uuid.uuid4())

        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.message_type, str):
            self.message_type = MessageType(self.message_type)
        if isinstance(self.priority, int):
            self.priority = Priority(self.priority)
        if isinstance(self.status_code, int):
            self.status_code = StatusCode(self.status_code)

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary following A2A protocol."""
        message_dict = {
            'role': self.role,
            'parts': [part.to_dict() for part in self.parts],
            'messageId': self.message_id,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'sender': self.sender,
            'recipients': self.recipients,
            'headers': self.headers.to_dict()
        }

        if self.status_code:
            message_dict['status_code'] = self.status_code.value
        if self.error_message:
            message_dict['error_message'] = self.error_message

        return message_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary with proper validation."""
        # Parse parts
        parts = []
        for part_data in data.get("parts", []):
            parts.append(A2AMessagePart.from_dict(part_data))

        # Parse headers
        headers_data = data.pop('headers', {})
        headers = A2AMessageHeaders.from_dict(headers_data)

        return cls(
            role=data["role"],
            parts=parts,
            message_id=data.get("messageId"),
            timestamp=data.get("timestamp"),
            message_type=data.get("message_type", MessageType.REQUEST),
            priority=data.get("priority", Priority.NORMAL),
            sender=data.get("sender", ""),
            recipients=data.get("recipients", []),
            headers=headers,
            status_code=data.get("status_code"),
            error_message=data.get("error_message")
        )

    def is_expired(self) -> bool:
        """Check if message has expired."""
        if not self.headers.expires_at:
            return False
        return datetime.now(UTC) > self.headers.expires_at

    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return self.headers.retry_count < self.headers.max_retries

    def increment_retry(self) -> None:
        """Increment retry count."""
        self.headers.retry_count += 1

    def add_custom_header(self, key: str, value: str) -> None:
        """Add custom header."""
        self.headers.custom_headers[key] = value

    def get_custom_header(self, key: str) -> str | None:
        """Get custom header value."""
        return self.headers.custom_headers.get(key)

    def validate(self) -> list[str]:
        """Validate message structure following A2A protocol."""
        errors = []

        if not self.role:
            errors.append("Role is required")

        if not self.parts:
            errors.append("At least one part is required")

        if not self.message_id:
            errors.append("Message ID is required")

        # Validate each part
        for part in self.parts:
            part_errors = part.validate()
            errors.extend(part_errors)

        if self.is_expired():
            errors.append("Message has expired")

        return errors


def create_text_message(role: str, text: str, message_id: str | None = None) -> A2AMessage:
    """Create a text message following A2A protocol."""
    text_part = A2AMessagePart(kind=PartType.TEXT, text=text)
    return A2AMessage(
        role=role,
        parts=[text_part],
        message_id=message_id
    )


def create_data_message(role: str, data: dict[str, Any], message_id: str | None = None) -> A2AMessage:
    """Create a data message following A2A protocol."""
    data_part = A2AMessagePart(kind=PartType.DATA, data=data)
    return A2AMessage(
        role=role,
        parts=[data_part],
        message_id=message_id
    )


def create_multipart_message(role: str, parts: list[A2AMessagePart], message_id: str | None = None) -> A2AMessage:
    """Create a multipart message following A2A protocol."""
    return A2AMessage(
        role=role,
        parts=parts,
        message_id=message_id
    )


def create_request_message(
    sender: str,
    recipients: list[str],
    parts: list[A2AMessagePart],
    message_type: MessageType = MessageType.REQUEST,
    priority: Priority = Priority.NORMAL,
    correlation_id: str | None = None
) -> A2AMessage:
    """Create a request message following A2A protocol."""
    headers = A2AMessageHeaders(
        correlation_id=correlation_id or str(uuid.uuid4()),
        expires_at=datetime.now(UTC).replace(microsecond=0) + timedelta(minutes=30)
    )

    return A2AMessage(
        role="user",
        parts=parts,
        message_type=message_type,
        priority=priority,
        sender=sender,
        recipients=recipients,
        headers=headers
    )


def create_response_message(
    original_message: A2AMessage,
    parts: list[A2AMessagePart],
    status_code: StatusCode = StatusCode.OK,
    error_message: str | None = None
) -> A2AMessage:
    """Create a response message following A2A protocol."""
    headers = A2AMessageHeaders(
        correlation_id=original_message.headers.correlation_id,
        reply_to=original_message.sender
    )

    return A2AMessage(
        role="assistant",
        parts=parts,
        message_type=MessageType.RESPONSE,
        priority=original_message.priority,
        sender=original_message.recipients[0] if original_message.recipients else "",
        recipients=[original_message.sender],
        headers=headers,
        status_code=status_code,
        error_message=error_message
    )


def create_error_message(
    original_message: A2AMessage,
    status_code: StatusCode,
    error_message: str
) -> A2AMessage:
    """Create an error message following A2A protocol."""
    error_part = A2AMessagePart(kind=PartType.TEXT, text=f"Error: {error_message}")
    return create_response_message(
        original_message=original_message,
        parts=[error_part],
        status_code=status_code,
        error_message=error_message
    )
