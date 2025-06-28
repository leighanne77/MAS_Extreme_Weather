"""
A2A Content Handlers

Implements content handlers for different part types in the A2A protocol.
"""

import base64
import json
from abc import ABC, abstractmethod
from typing import Any

from .parts import A2APart


class ContentHandler(ABC):
    """Abstract base class for content handlers."""

    @abstractmethod
    def can_handle(self, content_type: str) -> bool:
        """Check if this handler can handle the given content type."""
        pass

    @abstractmethod
    def serialize(self, content: Any) -> str:
        """Serialize content to string."""
        pass

    @abstractmethod
    def deserialize(self, content: str) -> Any:
        """Deserialize content from string."""
        pass

    @abstractmethod
    def validate(self, content: Any) -> list[str]:
        """Validate content and return list of errors."""
        pass


class TextHandler(ContentHandler):
    """Handler for text content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this handler can handle text content."""
        return content_type.startswith('text/')

    def serialize(self, content: Any) -> str:
        """Serialize text content."""
        if isinstance(content, str):
            return content
        return str(content)

    def deserialize(self, content: str) -> str:
        """Deserialize text content."""
        return content

    def validate(self, content: Any) -> list[str]:
        """Validate text content."""
        errors = []
        if not isinstance(content, str):
            errors.append("Content must be a string")
        if not content.strip():
            errors.append("Content cannot be empty")
        return errors


class DataHandler(ContentHandler):
    """Handler for structured data content (JSON, XML, etc.)."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this handler can handle data content."""
        return content_type in [
            'application/json',
            'application/xml',
            'application/yaml',
            'text/csv'
        ]

    def serialize(self, content: Any) -> str:
        """Serialize data content to JSON."""
        if isinstance(content, str):
            return content
        return json.dumps(content, indent=2)

    def deserialize(self, content: str) -> Any:
        """Deserialize data content from JSON."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    def validate(self, content: Any) -> list[str]:
        """Validate data content."""
        errors = []
        if content is None:
            errors.append("Content cannot be None")
        return errors


class FileHandler(ContentHandler):
    """Handler for file content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this handler can handle file content."""
        return content_type.startswith('application/') or \
               content_type.startswith('image/') or \
               content_type.startswith('audio/') or \
               content_type.startswith('video/')

    def serialize(self, content: Any) -> str:
        """Serialize file content to base64."""
        if isinstance(content, bytes):
            return base64.b64encode(content).decode('utf-8')
        elif isinstance(content, str):
            return content
        else:
            return base64.b64encode(str(content).encode('utf-8')).decode('utf-8')

    def deserialize(self, content: str) -> bytes:
        """Deserialize file content from base64."""
        try:
            return base64.b64decode(content)
        except Exception:
            return content.encode('utf-8')

    def validate(self, content: Any) -> list[str]:
        """Validate file content."""
        errors = []
        if content is None:
            errors.append("Content cannot be None")
        return errors


class ImageHandler(ContentHandler):
    """Handler for image content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this handler can handle image content."""
        return content_type.startswith('image/')

    def serialize(self, content: Any) -> str:
        """Serialize image content to base64."""
        if isinstance(content, bytes):
            return base64.b64encode(content).decode('utf-8')
        elif isinstance(content, str):
            return content
        else:
            return base64.b64encode(str(content).encode('utf-8')).decode('utf-8')

    def deserialize(self, content: str) -> bytes:
        """Deserialize image content from base64."""
        try:
            return base64.b64decode(content)
        except Exception:
            return content.encode('utf-8')

    def validate(self, content: Any) -> list[str]:
        """Validate image content."""
        errors = []
        if content is None:
            errors.append("Content cannot be None")
        return errors


class AudioHandler(ContentHandler):
    """Handler for audio content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this handler can handle audio content."""
        return content_type.startswith('audio/')

    def serialize(self, content: Any) -> str:
        """Serialize audio content to base64."""
        if isinstance(content, bytes):
            return base64.b64encode(content).decode('utf-8')
        elif isinstance(content, str):
            return content
        else:
            return base64.b64encode(str(content).encode('utf-8')).decode('utf-8')

    def deserialize(self, content: str) -> bytes:
        """Deserialize audio content from base64."""
        try:
            return base64.b64decode(content)
        except Exception:
            return content.encode('utf-8')

    def validate(self, content: Any) -> list[str]:
        """Validate audio content."""
        errors = []
        if content is None:
            errors.append("Content cannot be None")
        return errors


class VideoHandler(ContentHandler):
    """Handler for video content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this handler can handle video content."""
        return content_type.startswith('video/')

    def serialize(self, content: Any) -> str:
        """Serialize video content to base64."""
        if isinstance(content, bytes):
            return base64.b64encode(content).decode('utf-8')
        elif isinstance(content, str):
            return content
        else:
            return base64.b64encode(str(content).encode('utf-8')).decode('utf-8')

    def deserialize(self, content: str) -> bytes:
        """Deserialize video content from base64."""
        try:
            return base64.b64decode(content)
        except Exception:
            return content.encode('utf-8')

    def validate(self, content: Any) -> list[str]:
        """Validate video content."""
        errors = []
        if content is None:
            errors.append("Content cannot be None")
        return errors


class ContentHandlerRegistry:
    """Registry for content handlers."""

    def __init__(self):
        self.handlers: list[ContentHandler] = [
            TextHandler(),
            DataHandler(),
            FileHandler(),
            ImageHandler(),
            AudioHandler(),
            VideoHandler()
        ]

    def get_handler(self, content_type: str) -> ContentHandler | None:
        """Get handler for content type."""
        for handler in self.handlers:
            if handler.can_handle(content_type):
                return handler
        return None

    def get_handler_for_part(self, part: A2APart) -> ContentHandler | None:
        """Get handler for part."""
        content_type = part.content_type if hasattr(part, 'content_type') else 'text/plain'
        return self.get_handler(content_type)

    def register_handler(self, handler: ContentHandler) -> None:
        """Register a new handler."""
        self.handlers.append(handler)

    def serialize_part_content(self, part: A2APart) -> str:
        """Serialize part content."""
        handler = self.get_handler_for_part(part)
        if handler:
            return handler.serialize(part.content)
        return str(part.content)

    def deserialize_part_content(self, part: A2APart) -> Any:
        """Deserialize part content."""
        handler = self.get_handler_for_part(part)
        if handler:
            return handler.deserialize(part.content)
        return part.content

    def validate_part_content(self, part: A2APart) -> list[str]:
        """Validate part content."""
        handler = self.get_handler_for_part(part)
        if handler:
            return handler.validate(part.content)
        return []


# Global content handler registry instance
content_handler_registry = ContentHandlerRegistry()
