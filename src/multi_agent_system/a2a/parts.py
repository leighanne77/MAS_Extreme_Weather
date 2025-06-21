"""
A2A Part Types

Implements part types and content handling for the A2A protocol.
"""

import base64
import json
import mimetypes
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from .enums import PartType


@dataclass
class A2APart:
    """A2A Message Part"""
    id: str
    part_type: PartType
    content: Union[str, bytes, Dict[str, Any]]
    content_type: str = "text/plain"
    encoding: str = "utf-8"
    filename: Optional[str] = None
    size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        if isinstance(self.part_type, str):
            self.part_type = PartType(self.part_type)
        
        # Set content type based on part type if not specified
        if self.content_type == "text/plain":
            if self.part_type == PartType.DATA:
                self.content_type = "application/json"
            elif self.part_type == PartType.IMAGE:
                self.content_type = "image/png"
            elif self.part_type == PartType.AUDIO:
                self.content_type = "audio/wav"
            elif self.part_type == PartType.VIDEO:
                self.content_type = "video/mp4"
            elif self.part_type == PartType.BINARY:
                self.content_type = "application/octet-stream"
        
        # Calculate size if not provided
        if self.size is None:
            if isinstance(self.content, str):
                self.size = len(self.content.encode(self.encoding))
            elif isinstance(self.content, bytes):
                self.size = len(self.content)
            elif isinstance(self.content, dict):
                self.size = len(json.dumps(self.content).encode(self.encoding))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert part to dictionary."""
        part_dict = {
            'id': self.id,
            'part_type': self.part_type.value,
            'content_type': self.content_type,
            'encoding': self.encoding,
            'size': self.size,
            'metadata': self.metadata
        }
        
        # Serialize content based on type
        if isinstance(self.content, str):
            part_dict['content'] = self.content
        elif isinstance(self.content, bytes):
            part_dict['content'] = base64.b64encode(self.content).decode('utf-8')
            part_dict['encoding'] = 'base64'
        elif isinstance(self.content, dict):
            part_dict['content'] = self.content
        else:
            part_dict['content'] = str(self.content)
        
        if self.filename:
            part_dict['filename'] = self.filename
            
        return part_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2APart':
        """Create part from dictionary."""
        content = data['content']
        
        # Deserialize content based on encoding
        if data.get('encoding') == 'base64':
            content = base64.b64decode(content)
        elif isinstance(content, str) and data.get('part_type') == PartType.DATA.value:
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                pass  # Keep as string if JSON parsing fails
        
        return cls(
            id=data['id'],
            part_type=data['part_type'],
            content=content,
            content_type=data.get('content_type', 'text/plain'),
            encoding=data.get('encoding', 'utf-8'),
            filename=data.get('filename'),
            size=data.get('size'),
            metadata=data.get('metadata', {})
        )
    
    def validate(self) -> List[str]:
        """Validate part structure."""
        errors = []
        
        if not self.id:
            errors.append("Part ID is required")
        
        if not self.content:
            errors.append("Part content is required")
        
        if self.size and self.size <= 0:
            errors.append("Part size must be positive")
        
        return errors
    
    def get_content_as_text(self) -> str:
        """Get content as text."""
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, bytes):
            return self.content.decode(self.encoding)
        elif isinstance(self.content, dict):
            return json.dumps(self.content, indent=2)
        else:
            return str(self.content)
    
    def get_content_as_bytes(self) -> bytes:
        """Get content as bytes."""
        if isinstance(self.content, bytes):
            return self.content
        elif isinstance(self.content, str):
            return self.content.encode(self.encoding)
        elif isinstance(self.content, dict):
            return json.dumps(self.content).encode(self.encoding)
        else:
            return str(self.content).encode(self.encoding)
    
    def get_content_as_dict(self) -> Optional[Dict[str, Any]]:
        """Get content as dictionary."""
        if isinstance(self.content, dict):
            return self.content
        elif isinstance(self.content, str):
            try:
                return json.loads(self.content)
            except json.JSONDecodeError:
                return None
        return None


def create_text_part(content: str, part_id: Optional[str] = None) -> A2APart:
    """Create a text part."""
    import uuid
    return A2APart(
        id=part_id or str(uuid.uuid4()),
        part_type=PartType.TEXT,
        content=content,
        content_type="text/plain"
    )


def create_data_part(content: Dict[str, Any], part_id: Optional[str] = None) -> A2APart:
    """Create a data part."""
    import uuid
    return A2APart(
        id=part_id or str(uuid.uuid4()),
        part_type=PartType.DATA,
        content=content,
        content_type="application/json"
    )


def create_file_part(
    file_path: str,
    part_id: Optional[str] = None,
    content_type: Optional[str] = None
) -> A2APart:
    """Create a file part."""
    import uuid
    import os
    
    with open(file_path, 'rb') as f:
        content = f.read()
    
    if content_type is None:
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"
    
    # Determine part type based on content type
    if content_type.startswith('image/'):
        part_type = PartType.IMAGE
    elif content_type.startswith('audio/'):
        part_type = PartType.AUDIO
    elif content_type.startswith('video/'):
        part_type = PartType.VIDEO
    else:
        part_type = PartType.FILE
    
    return A2APart(
        id=part_id or str(uuid.uuid4()),
        part_type=part_type,
        content=content,
        content_type=content_type,
        filename=os.path.basename(file_path)
    )


def create_binary_part(
    content: bytes,
    content_type: str = "application/octet-stream",
    part_id: Optional[str] = None
) -> A2APart:
    """Create a binary part."""
    import uuid
    return A2APart(
        id=part_id or str(uuid.uuid4()),
        part_type=PartType.BINARY,
        content=content,
        content_type=content_type
    ) 