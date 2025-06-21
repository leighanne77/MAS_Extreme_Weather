"""
A2A Artifact System

Implements A2A-compliant artifact generation, management, and lifecycle.
"""

import uuid
import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

from .enums import StatusCode


class ArtifactType(Enum):
    """A2A Artifact Types"""
    REPORT = "report"
    RECOMMENDATION = "recommendation"
    VISUALIZATION = "visualization"
    DATA_EXPORT = "data_export"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    NOTIFICATION = "notification"
    AUDIT_LOG = "audit_log"


class ArtifactStatus(Enum):
    """A2A Artifact Status"""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    DELETED = "deleted"


class ArtifactPriority(Enum):
    """A2A Artifact Priority"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class ArtifactMetadata:
    """A2A Artifact Metadata"""
    title: str
    description: str
    author: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    accessed_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    language: str = "en"
    format: str = "json"
    size: int = 0
    checksum: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        metadata = asdict(self)
        if self.accessed_at:
            metadata['accessed_at'] = self.accessed_at.isoformat()
        metadata['created_at'] = self.created_at.isoformat()
        metadata['modified_at'] = self.modified_at.isoformat()
        return metadata
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtifactMetadata':
        """Create metadata from dictionary."""
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'modified_at' in data:
            data['modified_at'] = datetime.fromisoformat(data['modified_at'])
        if 'accessed_at' in data and data['accessed_at']:
            data['accessed_at'] = datetime.fromisoformat(data['accessed_at'])
        return cls(**data)


@dataclass
class ArtifactVersion:
    """A2A Artifact Version"""
    version: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    author: str = ""
    changes: List[str] = field(default_factory=list)
    content_hash: str = ""
    size: int = 0
    metadata: Optional[ArtifactMetadata] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary."""
        version_dict = asdict(self)
        version_dict['created_at'] = self.created_at.isoformat()
        if self.metadata:
            version_dict['metadata'] = self.metadata.to_dict()
        return version_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtifactVersion':
        """Create version from dictionary."""
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'metadata' in data and data['metadata']:
            data['metadata'] = ArtifactMetadata.from_dict(data['metadata'])
        return cls(**data)


@dataclass
class A2AArtifact:
    """A2A Artifact with full lifecycle management."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    artifact_type: ArtifactType = ArtifactType.REPORT
    status: ArtifactStatus = ArtifactStatus.DRAFT
    priority: ArtifactPriority = ArtifactPriority.NORMAL
    content: Union[str, Dict[str, Any], bytes] = ""
    metadata: ArtifactMetadata = field(default_factory=ArtifactMetadata)
    versions: List[ArtifactVersion] = field(default_factory=list)
    current_version: str = "1.0.0"
    expires_at: Optional[datetime] = None
    access_count: int = 0
    quality_score: float = 0.0
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup."""
        if isinstance(self.artifact_type, str):
            self.artifact_type = ArtifactType(self.artifact_type)
        if isinstance(self.status, str):
            self.status = ArtifactStatus(self.status)
        if isinstance(self.priority, int):
            self.priority = ArtifactPriority(self.priority)
        
        # Set default metadata if not provided
        if not self.metadata.title:
            self.metadata.title = f"{self.artifact_type.value.title()} Artifact"
        
        # Calculate content hash and size
        self._update_content_metrics()
        
        # Create initial version
        if not self.versions:
            self._create_initial_version()
    
    def _update_content_metrics(self):
        """Update content hash and size."""
        if isinstance(self.content, str):
            content_bytes = self.content.encode('utf-8')
        elif isinstance(self.content, dict):
            content_bytes = json.dumps(self.content, sort_keys=True).encode('utf-8')
        elif isinstance(self.content, bytes):
            content_bytes = self.content
        else:
            content_bytes = str(self.content).encode('utf-8')
        
        self.metadata.size = len(content_bytes)
        self.metadata.checksum = hashlib.sha256(content_bytes).hexdigest()
    
    def _create_initial_version(self):
        """Create initial version."""
        version = ArtifactVersion(
            version=self.current_version,
            author=self.metadata.author,
            content_hash=self.metadata.checksum,
            size=self.metadata.size,
            metadata=self.metadata
        )
        self.versions.append(version)
    
    def create_new_version(self, author: str, changes: List[str]) -> str:
        """Create a new version of the artifact."""
        # Increment version number
        major, minor, patch = map(int, self.current_version.split('.'))
        patch += 1
        new_version = f"{major}.{minor}.{patch}"
        
        # Update content metrics
        self._update_content_metrics()
        
        # Create new version
        version = ArtifactVersion(
            version=new_version,
            author=author,
            changes=changes,
            content_hash=self.metadata.checksum,
            size=self.metadata.size,
            metadata=self.metadata
        )
        
        self.versions.append(version)
        self.current_version = new_version
        self.metadata.modified_at = datetime.now(timezone.utc)
        
        return new_version
    
    def update_content(self, content: Union[str, Dict[str, Any], bytes], author: str, changes: List[str]):
        """Update artifact content and create new version."""
        self.content = content
        self.create_new_version(author, changes)
    
    def update_status(self, status: ArtifactStatus, author: str):
        """Update artifact status."""
        if isinstance(status, str):
            status = ArtifactStatus(status)
        
        self.status = status
        self.metadata.modified_at = datetime.now(timezone.utc)
        
        # Add status change to version history
        if self.versions:
            self.versions[-1].changes.append(f"Status changed to {status.value}")
    
    def update_metadata(self, metadata_updates: Dict[str, Any], author: str):
        """Update artifact metadata."""
        for key, value in metadata_updates.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
        
        self.metadata.modified_at = datetime.now(timezone.utc)
        self.create_new_version(author, ["Metadata updated"])
    
    def access(self, user_id: str):
        """Record artifact access."""
        self.access_count += 1
        self.metadata.accessed_at = datetime.now(timezone.utc)
    
    def is_expired(self) -> bool:
        """Check if artifact has expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def get_version(self, version: str) -> Optional[ArtifactVersion]:
        """Get specific version of the artifact."""
        for v in self.versions:
            if v.version == version:
                return v
        return None
    
    def rollback_to_version(self, version: str, author: str) -> bool:
        """Rollback to a specific version."""
        target_version = self.get_version(version)
        if not target_version:
            return False
        
        # Restore content and metadata from target version
        if target_version.metadata:
            self.metadata = target_version.metadata
            self.metadata.modified_at = datetime.now(timezone.utc)
        
        self.current_version = version
        self.create_new_version(author, [f"Rolled back to version {version}"])
        return True
    
    def calculate_quality_score(self) -> float:
        """Calculate artifact quality score."""
        score = 0.0
        
        # Content completeness
        if self.content:
            score += 20.0
        
        # Metadata completeness
        if self.metadata.title and self.metadata.description:
            score += 15.0
        
        # Version history
        if len(self.versions) > 1:
            score += 10.0
        
        # Access count (indicates usefulness)
        if self.access_count > 0:
            score += min(10.0, self.access_count * 0.1)
        
        # Status (published artifacts score higher)
        if self.status == ArtifactStatus.PUBLISHED:
            score += 20.0
        elif self.status == ArtifactStatus.REVIEW:
            score += 15.0
        
        # Tags and categorization
        if self.metadata.tags:
            score += min(10.0, len(self.metadata.tags) * 2.0)
        
        # Custom fields (indicates richness)
        if self.metadata.custom_fields:
            score += min(15.0, len(self.metadata.custom_fields) * 1.5)
        
        self.quality_score = min(100.0, score)
        return self.quality_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary."""
        artifact_dict = {
            'id': self.id,
            'artifact_type': self.artifact_type.value,
            'status': self.status.value,
            'priority': self.priority.value,
            'content': self.content,
            'metadata': self.metadata.to_dict(),
            'versions': [v.to_dict() for v in self.versions],
            'current_version': self.current_version,
            'access_count': self.access_count,
            'quality_score': self.quality_score,
            'permissions': self.permissions
        }
        
        if self.expires_at:
            artifact_dict['expires_at'] = self.expires_at.isoformat()
        
        return artifact_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AArtifact':
        """Create artifact from dictionary."""
        if 'expires_at' in data and data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        # Convert versions
        versions_data = data.pop('versions', [])
        data['versions'] = [ArtifactVersion.from_dict(v) for v in versions_data]
        
        # Convert metadata
        metadata_data = data.pop('metadata', {})
        data['metadata'] = ArtifactMetadata.from_dict(metadata_data)
        
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate artifact structure."""
        errors = []
        
        if not self.id:
            errors.append("Artifact ID is required")
        
        if not self.metadata.title:
            errors.append("Artifact title is required")
        
        if not self.content:
            errors.append("Artifact content is required")
        
        if self.is_expired():
            errors.append("Artifact has expired")
        
        return errors


def create_artifact(
    artifact_type: ArtifactType,
    content: Union[str, Dict[str, Any], bytes],
    title: str,
    description: str,
    author: str,
    tags: Optional[List[str]] = None,
    priority: ArtifactPriority = ArtifactPriority.NORMAL
) -> A2AArtifact:
    """Create a new A2A artifact."""
    metadata = ArtifactMetadata(
        title=title,
        description=description,
        author=author,
        tags=tags or []
    )
    
    return A2AArtifact(
        artifact_type=artifact_type,
        content=content,
        metadata=metadata,
        priority=priority
    )


def create_report_artifact(
    content: Dict[str, Any],
    title: str,
    description: str,
    author: str,
    tags: Optional[List[str]] = None
) -> A2AArtifact:
    """Create a report artifact."""
    return create_artifact(
        artifact_type=ArtifactType.REPORT,
        content=content,
        title=title,
        description=description,
        author=author,
        tags=tags
    )


def create_recommendation_artifact(
    content: Dict[str, Any],
    title: str,
    description: str,
    author: str,
    tags: Optional[List[str]] = None
) -> A2AArtifact:
    """Create a recommendation artifact."""
    return create_artifact(
        artifact_type=ArtifactType.RECOMMENDATION,
        content=content,
        title=title,
        description=description,
        author=author,
        tags=tags
    )


def create_visualization_artifact(
    content: bytes,
    title: str,
    description: str,
    author: str,
    format: str = "png",
    tags: Optional[List[str]] = None
) -> A2AArtifact:
    """Create a visualization artifact."""
    metadata = ArtifactMetadata(
        title=title,
        description=description,
        author=author,
        format=format,
        tags=tags or []
    )
    
    return A2AArtifact(
        artifact_type=ArtifactType.VISUALIZATION,
        content=content,
        metadata=metadata
    ) 