"""
A2A Artifact Manager

Manages A2A artifact storage, retrieval, and lifecycle operations.
"""

import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict
import sqlite3
from contextlib import contextmanager

from .artifacts import (
    A2AArtifact, ArtifactType, ArtifactStatus, ArtifactPriority,
    ArtifactMetadata, ArtifactVersion
)
from .enums import StatusCode


class ArtifactStorageError(Exception):
    """Raised when artifact storage operations fail."""
    pass


class ArtifactNotFoundError(Exception):
    """Raised when an artifact is not found."""
    pass


class ArtifactPermissionError(Exception):
    """Raised when user lacks permission to access artifact."""
    pass


class A2AArtifactManager:
    """Manages A2A artifacts with full lifecycle support."""
    
    def __init__(self, storage_path: str = "artifacts", db_path: str = "artifacts.db"):
        """Initialize artifact manager."""
        self.storage_path = Path(storage_path)
        self.db_path = Path(db_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Cache for frequently accessed artifacts
        self._cache: Dict[str, A2AArtifact] = {}
        self._cache_size = 100
    
    def _init_database(self):
        """Initialize SQLite database for artifact metadata."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    artifact_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    author TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    modified_at TEXT NOT NULL,
                    accessed_at TEXT,
                    current_version TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    quality_score REAL DEFAULT 0.0,
                    expires_at TEXT,
                    tags TEXT,
                    custom_fields TEXT,
                    content_path TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifact_versions (
                    artifact_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    author TEXT NOT NULL,
                    changes TEXT,
                    content_hash TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    PRIMARY KEY (artifact_id, version),
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifact_permissions (
                    artifact_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    granted_at TEXT NOT NULL,
                    granted_by TEXT NOT NULL,
                    PRIMARY KEY (artifact_id, user_id),
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_author ON artifacts(author)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_created ON artifacts(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_tags ON artifacts(tags)")
    
    @contextmanager
    def _get_db_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            raise ArtifactStorageError(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
    
    def store_artifact(self, artifact: A2AArtifact) -> str:
        """Store an artifact in the system."""
        try:
            # Validate artifact
            errors = artifact.validate()
            if errors:
                raise ArtifactStorageError(f"Invalid artifact: {', '.join(errors)}")
            
            # Store content file
            content_path = self._store_content(artifact)
            
            # Store metadata in database
            with self._get_db_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO artifacts (
                        id, artifact_type, status, priority, title, description,
                        author, created_at, modified_at, accessed_at, current_version,
                        access_count, quality_score, expires_at, tags, custom_fields, content_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    artifact.id,
                    artifact.artifact_type.value,
                    artifact.status.value,
                    artifact.priority.value,
                    artifact.metadata.title,
                    artifact.metadata.description,
                    artifact.metadata.author,
                    artifact.metadata.created_at.isoformat(),
                    artifact.metadata.modified_at.isoformat(),
                    artifact.metadata.accessed_at.isoformat() if artifact.metadata.accessed_at else None,
                    artifact.current_version,
                    artifact.access_count,
                    artifact.quality_score,
                    artifact.expires_at.isoformat() if artifact.expires_at else None,
                    json.dumps(artifact.metadata.tags),
                    json.dumps(artifact.metadata.custom_fields),
                    content_path
                ))
                
                # Store versions
                for version in artifact.versions:
                    conn.execute("""
                        INSERT OR REPLACE INTO artifact_versions (
                            artifact_id, version, created_at, author, changes, content_hash, size
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        artifact.id,
                        version.version,
                        version.created_at.isoformat(),
                        version.author,
                        json.dumps(version.changes),
                        version.content_hash,
                        version.size
                    ))
                
                # Store permissions
                for user_id, permissions in artifact.permissions.items():
                    conn.execute("""
                        INSERT OR REPLACE INTO artifact_permissions (
                            artifact_id, user_id, permissions, granted_at, granted_by
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        artifact.id,
                        user_id,
                        json.dumps(permissions),
                        datetime.utcnow().isoformat(),
                        artifact.metadata.author
                    ))
                
                conn.commit()
            
            # Update cache
            self._update_cache(artifact)
            
            return artifact.id
            
        except Exception as e:
            raise ArtifactStorageError(f"Failed to store artifact: {e}")
    
    def _store_content(self, artifact: A2AArtifact) -> str:
        """Store artifact content to file system."""
        content_dir = self.storage_path / artifact.id
        content_dir.mkdir(exist_ok=True)
        
        content_path = content_dir / f"content_{artifact.current_version}.{artifact.metadata.format}"
        
        if isinstance(artifact.content, str):
            content_path.write_text(artifact.content, encoding='utf-8')
        elif isinstance(artifact.content, dict):
            content_path.write_text(json.dumps(artifact.content, indent=2), encoding='utf-8')
        elif isinstance(artifact.content, bytes):
            content_path.write_bytes(artifact.content)
        else:
            content_path.write_text(str(artifact.content), encoding='utf-8')
        
        return str(content_path.relative_to(self.storage_path))
    
    def retrieve_artifact(self, artifact_id: str, user_id: Optional[str] = None) -> A2AArtifact:
        """Retrieve an artifact by ID."""
        # Check cache first
        if artifact_id in self._cache:
            artifact = self._cache[artifact_id]
            artifact.access(user_id or "unknown")
            return artifact
        
        try:
            with self._get_db_connection() as conn:
                # Get artifact metadata
                row = conn.execute("""
                    SELECT * FROM artifacts WHERE id = ?
                """, (artifact_id,)).fetchone()
                
                if not row:
                    raise ArtifactNotFoundError(f"Artifact {artifact_id} not found")
                
                # Check permissions
                if user_id:
                    self._check_permissions(conn, artifact_id, user_id)
                
                # Load content
                content_path = self.storage_path / row['content_path']
                content = self._load_content(content_path, row['artifact_type'])
                
                # Create metadata
                metadata = ArtifactMetadata(
                    title=row['title'],
                    description=row['description'],
                    author=row['author'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    modified_at=datetime.fromisoformat(row['modified_at']),
                    accessed_at=datetime.fromisoformat(row['accessed_at']) if row['accessed_at'] else None,
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    custom_fields=json.loads(row['custom_fields']) if row['custom_fields'] else {}
                )
                
                # Load versions
                versions = []
                version_rows = conn.execute("""
                    SELECT * FROM artifact_versions WHERE artifact_id = ? ORDER BY created_at
                """, (artifact_id,)).fetchall()
                
                for v_row in version_rows:
                    version = ArtifactVersion(
                        version=v_row['version'],
                        created_at=datetime.fromisoformat(v_row['created_at']),
                        author=v_row['author'],
                        changes=json.loads(v_row['changes']) if v_row['changes'] else [],
                        content_hash=v_row['content_hash'],
                        size=v_row['size']
                    )
                    versions.append(version)
                
                # Load permissions
                permissions = {}
                perm_rows = conn.execute("""
                    SELECT user_id, permissions FROM artifact_permissions WHERE artifact_id = ?
                """, (artifact_id,)).fetchall()
                
                for p_row in perm_rows:
                    permissions[p_row['user_id']] = json.loads(p_row['permissions'])
                
                # Create artifact
                artifact = A2AArtifact(
                    id=artifact_id,
                    artifact_type=ArtifactType(row['artifact_type']),
                    status=ArtifactStatus(row['status']),
                    priority=ArtifactPriority(row['priority']),
                    content=content,
                    metadata=metadata,
                    versions=versions,
                    current_version=row['current_version'],
                    access_count=row['access_count'],
                    quality_score=row['quality_score'],
                    permissions=permissions
                )
                
                if row['expires_at']:
                    artifact.expires_at = datetime.fromisoformat(row['expires_at'])
                
                # Update access count
                artifact.access(user_id or "unknown")
                self.store_artifact(artifact)
                
                # Update cache
                self._update_cache(artifact)
                
                return artifact
                
        except ArtifactNotFoundError:
            raise
        except Exception as e:
            raise ArtifactStorageError(f"Failed to retrieve artifact: {e}")
    
    def _load_content(self, content_path: Path, artifact_type: str) -> Union[str, Dict[str, Any], bytes]:
        """Load artifact content from file."""
        if not content_path.exists():
            raise ArtifactStorageError(f"Content file not found: {content_path}")
        
        if artifact_type == ArtifactType.VISUALIZATION.value:
            return content_path.read_bytes()
        elif content_path.suffix == '.json':
            return json.loads(content_path.read_text(encoding='utf-8'))
        else:
            return content_path.read_text(encoding='utf-8')
    
    def _check_permissions(self, conn, artifact_id: str, user_id: str):
        """Check if user has permission to access artifact."""
        # For now, allow all access - implement proper permission checking later
        pass
    
    def search_artifacts(
        self,
        artifact_type: Optional[ArtifactType] = None,
        status: Optional[ArtifactStatus] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[A2AArtifact]:
        """Search artifacts with filters."""
        try:
            query = "SELECT id FROM artifacts WHERE 1=1"
            params = []
            
            if artifact_type:
                query += " AND artifact_type = ?"
                params.append(artifact_type.value)
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if author:
                query += " AND author = ?"
                params.append(author)
            
            if tags:
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f'%"{tag}"%')
            
            if created_after:
                query += " AND created_at >= ?"
                params.append(created_after.isoformat())
            
            if created_before:
                query += " AND created_at <= ?"
                params.append(created_before.isoformat())
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            with self._get_db_connection() as conn:
                rows = conn.execute(query, params).fetchall()
                
                artifacts = []
                for row in rows:
                    try:
                        artifact = self.retrieve_artifact(row['id'])
                        artifacts.append(artifact)
                    except Exception as e:
                        # Log error but continue with other artifacts
                        print(f"Error loading artifact {row['id']}: {e}")
                
                return artifacts
                
        except Exception as e:
            raise ArtifactStorageError(f"Failed to search artifacts: {e}")
    
    def update_artifact(
        self,
        artifact_id: str,
        updates: Dict[str, Any],
        author: str,
        user_id: Optional[str] = None
    ) -> A2AArtifact:
        """Update an existing artifact."""
        artifact = self.retrieve_artifact(artifact_id, user_id)
        
        # Apply updates
        if 'content' in updates:
            artifact.update_content(updates['content'], author, updates.get('changes', ['Content updated']))
        
        if 'status' in updates:
            artifact.update_status(updates['status'], author)
        
        if 'metadata' in updates:
            artifact.update_metadata(updates['metadata'], author)
        
        if 'priority' in updates:
            artifact.priority = ArtifactPriority(updates['priority'])
        
        if 'expires_at' in updates:
            artifact.expires_at = datetime.fromisoformat(updates['expires_at']) if updates['expires_at'] else None
        
        # Store updated artifact
        self.store_artifact(artifact)
        
        return artifact
    
    def delete_artifact(self, artifact_id: str, user_id: Optional[str] = None) -> bool:
        """Delete an artifact (soft delete by default)."""
        try:
            artifact = self.retrieve_artifact(artifact_id, user_id)
            
            # Soft delete - change status to deleted
            artifact.update_status(ArtifactStatus.DELETED, user_id or "system")
            self.store_artifact(artifact)
            
            # Remove from cache
            if artifact_id in self._cache:
                del self._cache[artifact_id]
            
            return True
            
        except Exception as e:
            raise ArtifactStorageError(f"Failed to delete artifact: {e}")
    
    def purge_artifact(self, artifact_id: str, user_id: Optional[str] = None) -> bool:
        """Permanently delete an artifact and all its data."""
        try:
            # Check if artifact exists
            with self._get_db_connection() as conn:
                row = conn.execute("SELECT content_path FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
                if not row:
                    return False
                
                # Delete from database
                conn.execute("DELETE FROM artifact_versions WHERE artifact_id = ?", (artifact_id,))
                conn.execute("DELETE FROM artifact_permissions WHERE artifact_id = ?", (artifact_id,))
                conn.execute("DELETE FROM artifacts WHERE id = ?", (artifact_id,))
                conn.commit()
            
            # Delete content files
            content_dir = self.storage_path / artifact_id
            if content_dir.exists():
                shutil.rmtree(content_dir)
            
            # Remove from cache
            if artifact_id in self._cache:
                del self._cache[artifact_id]
            
            return True
            
        except Exception as e:
            raise ArtifactStorageError(f"Failed to purge artifact: {e}")
    
    def get_artifact_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored artifacts."""
        try:
            with self._get_db_connection() as conn:
                stats = {}
                
                # Total artifacts
                total = conn.execute("SELECT COUNT(*) as count FROM artifacts").fetchone()['count']
                stats['total_artifacts'] = total
                
                # By type
                type_stats = conn.execute("""
                    SELECT artifact_type, COUNT(*) as count 
                    FROM artifacts 
                    GROUP BY artifact_type
                """).fetchall()
                stats['by_type'] = {row['artifact_type']: row['count'] for row in type_stats}
                
                # By status
                status_stats = conn.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM artifacts 
                    GROUP BY status
                """).fetchall()
                stats['by_status'] = {row['status']: row['count'] for row in status_stats}
                
                # By author
                author_stats = conn.execute("""
                    SELECT author, COUNT(*) as count 
                    FROM artifacts 
                    GROUP BY author 
                    ORDER BY count DESC 
                    LIMIT 10
                """).fetchall()
                stats['by_author'] = {row['author']: row['count'] for row in author_stats}
                
                # Storage size
                size_stats = conn.execute("""
                    SELECT SUM(size) as total_size, AVG(size) as avg_size 
                    FROM artifacts
                """).fetchone()
                stats['storage'] = {
                    'total_size': size_stats['total_size'] or 0,
                    'average_size': size_stats['avg_size'] or 0
                }
                
                return stats
                
        except Exception as e:
            raise ArtifactStorageError(f"Failed to get statistics: {e}")
    
    def cleanup_expired_artifacts(self) -> int:
        """Remove expired artifacts."""
        try:
            with self._get_db_connection() as conn:
                expired = conn.execute("""
                    SELECT id FROM artifacts 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (datetime.utcnow().isoformat(),)).fetchall()
                
                count = 0
                for row in expired:
                    try:
                        self.purge_artifact(row['id'])
                        count += 1
                    except Exception as e:
                        print(f"Error purging expired artifact {row['id']}: {e}")
                
                return count
                
        except Exception as e:
            raise ArtifactStorageError(f"Failed to cleanup expired artifacts: {e}")
    
    def _update_cache(self, artifact: A2AArtifact):
        """Update artifact cache."""
        self._cache[artifact.id] = artifact
        
        # Maintain cache size
        if len(self._cache) > self._cache_size:
            # Remove oldest entries (simple LRU)
            oldest_keys = list(self._cache.keys())[:len(self._cache) - self._cache_size]
            for key in oldest_keys:
                del self._cache[key]
    
    def clear_cache(self):
        """Clear the artifact cache."""
        self._cache.clear()
    
    def export_artifacts(self, artifact_ids: List[str], export_path: str) -> str:
        """Export artifacts to a file."""
        try:
            export_data = {
                'exported_at': datetime.utcnow().isoformat(),
                'artifacts': []
            }
            
            for artifact_id in artifact_ids:
                try:
                    artifact = self.retrieve_artifact(artifact_id)
                    export_data['artifacts'].append(artifact.to_dict())
                except Exception as e:
                    print(f"Error exporting artifact {artifact_id}: {e}")
            
            export_file = Path(export_path)
            export_file.write_text(json.dumps(export_data, indent=2), encoding='utf-8')
            
            return str(export_file)
            
        except Exception as e:
            raise ArtifactStorageError(f"Failed to export artifacts: {e}")
    
    def import_artifacts(self, import_path: str, overwrite: bool = False) -> List[str]:
        """Import artifacts from a file."""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                raise ArtifactStorageError(f"Import file not found: {import_path}")
            
            import_data = json.loads(import_file.read_text(encoding='utf-8'))
            imported_ids = []
            
            for artifact_data in import_data.get('artifacts', []):
                try:
                    artifact = A2AArtifact.from_dict(artifact_data)
                    
                    # Check if artifact already exists
                    if not overwrite:
                        try:
                            existing = self.retrieve_artifact(artifact.id)
                            if existing:
                                print(f"Skipping existing artifact {artifact.id}")
                                continue
                        except ArtifactNotFoundError:
                            pass
                    
                    self.store_artifact(artifact)
                    imported_ids.append(artifact.id)
                    
                except Exception as e:
                    print(f"Error importing artifact: {e}")
            
            return imported_ids
            
        except Exception as e:
            raise ArtifactStorageError(f"Failed to import artifacts: {e}")


# Global artifact manager instance
artifact_manager = A2AArtifactManager() 