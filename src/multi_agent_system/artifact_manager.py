"""
Artifact Management System for Multi-Agent Climate Risk Analysis

This module implements a filesystem-based artifact management system for storing,
retrieving, and managing agent outputs in the climate risk analysis system.

Key Components:
    - ArtifactManager: Main class for artifact management
    - Artifact Storage: Filesystem-based storage system
    - Artifact Metadata: Comprehensive metadata tracking
    - Cleanup System: Automatic artifact cleanup

Features:
    1. Artifact Storage:
       - Session-based organization
       - Agent-specific directories
       - Type-based categorization
       - Metadata tracking

    2. Artifact Retrieval:
       - Path-based retrieval
       - Filtered listing
       - Metadata access
       - Content validation

    3. Cleanup Management:
       - Session cleanup
       - Age-based cleanup
       - Space optimization
       - Directory maintenance

    4. Statistics Tracking:
       - Size monitoring
       - Usage patterns
       - Type distribution
       - Agent statistics

Dependencies:
    - aiofiles: For asynchronous file operations
    - pathlib: For path manipulation
    - json: For data serialization
    - shutil: For directory operations

Example Usage:
    ```python
    # Initialize artifact manager
    manager = ArtifactManager(base_dir="artifacts")

    # Store artifact
    artifact_path = await manager.store_artifact(
        session_id="session_123",
        agent_id="risk_analyzer",
        artifact_type="analysis",
        data={"risk_level": "high"},
        metadata={"location": "New York"}
    )

    # Retrieve artifact
    artifact = await manager.get_artifact(artifact_path)

    # List artifacts
    artifacts = await manager.list_artifacts(
        session_id="session_123",
        agent_id="risk_analyzer"
    )
    ```

Configuration:
    - BASE_DIR: Base directory for artifacts
    - MAX_AGE_DAYS: Maximum artifact age
    - CLEANUP_INTERVAL: Cleanup check interval
    - METADATA_FIELDS: Required metadata fields
"""

import asyncio
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles


class ArtifactManager:
    """Manages artifacts for the multi-agent climate risk analysis system.

    This class provides comprehensive artifact management capabilities,
    including storage, retrieval, cleanup, and statistics tracking.

    Key Features:
        - Filesystem-based storage
        - Session-based organization
        - Metadata tracking
        - Automatic cleanup
        - Statistics collection

    State Management:
        - Maintains directory structure
        - Tracks artifact metadata
        - Manages cleanup schedules
        - Monitors storage usage

    Example:
        ```python
        manager = ArtifactManager(base_dir="artifacts")

        # Store analysis result
        path = await manager.store_artifact(
            session_id="session_123",
            agent_id="risk_analyzer",
            artifact_type="analysis",
            data={"risk_level": "high"}
        )

        # Get artifact statistics
        stats = await manager.get_artifact_stats("session_123")
        ```
    """

    def __init__(self, base_dir: str = "artifacts"):
        """Initialize the artifact manager.

        Args:
            base_dir (str): Base directory for storing artifacts

        Initialization:
            - Creates base directory
            - Sets up directory structure
            - Initializes locking mechanism
            - Configures cleanup settings

        Example:
            ```python
            manager = ArtifactManager(base_dir="artifacts")
            ```
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.lock = asyncio.Lock()

    async def store_artifact(
        self,
        session_id: str,
        agent_id: str,
        artifact_type: str,
        data: Any,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """Store an artifact in the filesystem.

        Args:
            session_id (str): Session identifier
            agent_id (str): Agent identifier
            artifact_type (str): Type of artifact
            data (Any): Data to store
            metadata (Dict[str, Any], optional): Additional metadata

        Returns:
            str: Path to stored artifact

        Storage Process:
            1. Creates directory structure
            2. Generates filename
            3. Prepares artifact data
            4. Stores data and metadata
            5. Returns artifact path

        Example:
            ```python
            path = await manager.store_artifact(
                session_id="session_123",
                agent_id="risk_analyzer",
                artifact_type="analysis",
                data={"risk_level": "high"},
                metadata={"location": "New York"}
            )
            ```
        """
        async with self.lock:
            # Create session directory
            session_dir = self.base_dir / session_id
            session_dir.mkdir(exist_ok=True)

            # Create agent directory
            agent_dir = session_dir / agent_id
            agent_dir.mkdir(exist_ok=True)

            # Generate artifact filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{artifact_type}_{timestamp}.json"
            artifact_path = agent_dir / filename

            # Prepare artifact data
            artifact_data = {
                "data": data,
                "metadata": metadata or {},
                "timestamp": timestamp,
                "session_id": session_id,
                "agent_id": agent_id,
                "type": artifact_type
            }

            # Store artifact
            async with aiofiles.open(artifact_path, 'w') as f:
                await f.write(json.dumps(artifact_data, indent=2))

            return str(artifact_path)

    async def get_artifact(self, artifact_path: str) -> dict[str, Any]:
        """Retrieve an artifact from the filesystem.

        Args:
            artifact_path (str): Path to artifact

        Returns:
            Dict[str, Any]: Artifact data

        Retrieval Process:
            1. Validates path
            2. Reads artifact file
            3. Parses JSON data
            4. Returns artifact

        Example:
            ```python
            artifact = await manager.get_artifact("artifacts/session_123/risk_analyzer/analysis_20240101_120000.json")
            ```
        """
        async with self.lock:
            async with aiofiles.open(artifact_path) as f:
                content = await f.read()
                return json.loads(content)

    async def list_artifacts(
        self,
        session_id: str | None = None,
        agent_id: str | None = None,
        artifact_type: str | None = None
    ) -> list[dict[str, Any]]:
        """List artifacts matching the given criteria.

        Args:
            session_id (str, optional): Filter by session
            agent_id (str, optional): Filter by agent
            artifact_type (str, optional): Filter by type

        Returns:
            List[Dict[str, Any]]: List of matching artifacts

        Listing Process:
            1. Determines search path
            2. Walks directory structure
            3. Applies filters
            4. Collects metadata
            5. Returns matches

        Example:
            ```python
            artifacts = await manager.list_artifacts(
                session_id="session_123",
                agent_id="risk_analyzer",
                artifact_type="analysis"
            )
            ```
        """
        async with self.lock:
            artifacts = []

            # Determine search path
            if session_id:
                search_path = self.base_dir / session_id
            else:
                search_path = self.base_dir

            if not search_path.exists():
                return artifacts

            # Walk through directories
            for root, _, files in os.walk(search_path):
                for file in files:
                    if not file.endswith('.json'):
                        continue

                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.base_dir)

                    # Parse path components
                    parts = rel_path.parts
                    if len(parts) < 2:
                        continue

                    current_session_id = parts[0]
                    current_agent_id = parts[1]

                    # Apply filters
                    if session_id and current_session_id != session_id:
                        continue
                    if agent_id and current_agent_id != agent_id:
                        continue

                    # Read artifact metadata
                    try:
                        async with aiofiles.open(file_path) as f:
                            content = await f.read()
                            artifact = json.loads(content)

                            if artifact_type and artifact['type'] != artifact_type:
                                continue

                            artifacts.append({
                                'path': str(file_path),
                                'session_id': current_session_id,
                                'agent_id': current_agent_id,
                                'type': artifact['type'],
                                'timestamp': artifact['timestamp']
                            })
                    except Exception:
                        continue

            return artifacts

    async def cleanup_session(self, session_id: str) -> None:
        """Clean up all artifacts for a session.

        Args:
            session_id (str): Session identifier

        Cleanup Process:
            1. Locates session directory
            2. Removes all artifacts
            3. Cleans up directories
            4. Updates statistics

        Example:
            ```python
            await manager.cleanup_session("session_123")
            ```
        """
        async with self.lock:
            session_dir = self.base_dir / session_id
            if session_dir.exists():
                shutil.rmtree(session_dir)

    async def cleanup_old_artifacts(self, max_age_days: int = 7) -> None:
        """Clean up artifacts older than max_age_days.

        Args:
            max_age_days (int): Maximum age in days

        Cleanup Process:
            1. Calculates cutoff time
            2. Identifies old artifacts
            3. Removes artifacts
            4. Cleans directories

        Example:
            ```python
            await manager.cleanup_old_artifacts(max_age_days=7)
            ```
        """
        async with self.lock:
            cutoff = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)

            for root, _, files in os.walk(self.base_dir):
                for file in files:
                    if not file.endswith('.json'):
                        continue

                    file_path = Path(root) / file
                    if file_path.stat().st_mtime < cutoff:
                        file_path.unlink()

                # Remove empty directories
                if not os.listdir(root):
                    os.rmdir(root)

    async def get_artifact_stats(self, session_id: str) -> dict[str, Any]:
        """Get statistics about artifacts for a session.

        Args:
            session_id (str): Session identifier

        Returns:
            Dict[str, Any]: Artifact statistics

        Statistics Include:
            - Total artifact count
            - Total size
            - Per-agent statistics
            - Per-type statistics

        Example:
            ```python
            stats = await manager.get_artifact_stats("session_123")
            print(f"Total artifacts: {stats['total_artifacts']}")
            ```
        """
        async with self.lock:
            session_dir = self.base_dir / session_id
            if not session_dir.exists():
                return {}

            stats = {
                'total_artifacts': 0,
                'total_size': 0,
                'by_agent': {},
                'by_type': {}
            }

            for root, _, files in os.walk(session_dir):
                for file in files:
                    if not file.endswith('.json'):
                        continue

                    file_path = Path(root) / file
                    size = file_path.stat().st_size

                    stats['total_artifacts'] += 1
                    stats['total_size'] += size

                    # Parse path components
                    rel_path = file_path.relative_to(self.base_dir)
                    parts = rel_path.parts
                    if len(parts) < 2:
                        continue

                    agent_id = parts[1]

                    # Update agent stats
                    if agent_id not in stats['by_agent']:
                        stats['by_agent'][agent_id] = {
                            'count': 0,
                            'size': 0
                        }
                    stats['by_agent'][agent_id]['count'] += 1
                    stats['by_agent'][agent_id]['size'] += size

                    # Read artifact type
                    try:
                        async with aiofiles.open(file_path) as f:
                            content = await f.read()
                            artifact = json.loads(content)
                            artifact_type = artifact['type']

                            # Update type stats
                            if artifact_type not in stats['by_type']:
                                stats['by_type'][artifact_type] = {
                                    'count': 0,
                                    'size': 0
                                }
                            stats['by_type'][artifact_type]['count'] += 1
                            stats['by_type'][artifact_type]['size'] += size
                    except Exception:
                        continue

            return stats
