"""
Data Catalog Agent Module

This module provides an agent for metadata management and data discovery.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles

from ..validators import SchemaValidator
from .base_agent import BaseAgent


class MetadataEntry(BaseModel):
    """Represents a metadata entry in the catalog."""
    id: str
    name: str
    description: str
    schema: dict[str, Any]
    tags: list[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    lineage: dict[str, Any] = {}
    quality_metrics: dict[str, float] = {}

class DataCatalogAgent(BaseAgent):
    """Agent responsible for metadata management and data discovery."""

    def __init__(
        self,
        agent_id: str,
        catalog_dir: str = "catalog",
        config: dict[str, Any] | None = None,
        schema_validator: SchemaValidator | None = None
    ):
        """Initialize the data catalog agent.

        Args:
            agent_id: Unique identifier for the agent
            catalog_dir: Directory for storing catalog metadata
            config: Optional configuration dictionary
            schema_validator: Optional SchemaValidator instance
        """
        super().__init__(agent_id, config)
        self.catalog_dir = Path(catalog_dir)
        self.catalog_dir.mkdir(parents=True, exist_ok=True)
        self.schema_validator = schema_validator or SchemaValidator()
        self.logger = logging.getLogger(f"catalog_agent.{agent_id}")

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute catalog operations.

        Args:
            context: Execution context containing operation details

        Returns:
            Dictionary containing operation results
        """
        try:
            await self.update_state("running")

            operation = context.get("operation")
            if not operation:
                raise ValueError("No operation specified in context")

            if operation == "register":
                result = await self._register_metadata(context)
            elif operation == "discover":
                result = await self._discover_metadata(context)
            elif operation == "update":
                result = await self._update_metadata(context)
            else:
                raise ValueError(f"Unknown operation: {operation}")

            await self.update_state("completed")
            return result

        except Exception as e:
            await self.handle_error(e)
            raise

    async def _register_metadata(self, context: dict[str, Any]) -> dict[str, Any]:
        """Register new metadata in the catalog.

        Args:
            context: Context containing metadata to register

        Returns:
            Registration result
        """
        metadata = context.get("metadata")
        if not metadata:
            raise ValueError("No metadata provided in context")

        # Validate schema if provided
        if "schema" in metadata:
            await self.schema_validator.validate_schema(metadata["schema"])

        # Create metadata entry
        entry = MetadataEntry(
            id=metadata.get("id", str(datetime.now().timestamp())),
            name=metadata["name"],
            description=metadata.get("description", ""),
            schema=metadata.get("schema", {}),
            tags=metadata.get("tags", []),
            lineage=metadata.get("lineage", {}),
            quality_metrics=metadata.get("quality_metrics", {})
        )

        # Save to catalog
        entry_path = self.catalog_dir / f"{entry.id}.json"
        async with aiofiles.open(entry_path, 'w') as f:
            await f.write(entry.json(indent=2))

        return {
            "status": "success",
            "entry_id": entry.id,
            "timestamp": datetime.now().isoformat()
        }

    async def _discover_metadata(
        self,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Discover metadata matching search criteria.

        Args:
            context: Context containing search criteria

        Returns:
            Search results
        """
        query = context.get("query", {})
        results = []

        # Search through catalog entries
        for entry_path in self.catalog_dir.glob("*.json"):
            async with aiofiles.open(entry_path) as f:
                entry_data = json.loads(await f.read())
                entry = MetadataEntry(**entry_data)

                # Apply search filters
                if self._matches_query(entry, query):
                    results.append(entry.dict())

        return {
            "status": "success",
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }

    async def _update_metadata(self, context: dict[str, Any]) -> dict[str, Any]:
        """Update existing metadata in the catalog.

        Args:
            context: Context containing update information

        Returns:
            Update result
        """
        entry_id = context.get("entry_id")
        if not entry_id:
            raise ValueError("No entry_id provided in context")

        updates = context.get("updates", {})
        if not updates:
            raise ValueError("No updates provided in context")

        # Load existing entry
        entry_path = self.catalog_dir / f"{entry_id}.json"
        if not entry_path.exists():
            raise ValueError(f"Entry not found: {entry_id}")

        async with aiofiles.open(entry_path) as f:
            entry_data = json.loads(await f.read())
            entry = MetadataEntry(**entry_data)

        # Apply updates
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        entry.updated_at = datetime.now()

        # Save updated entry
        async with aiofiles.open(entry_path, 'w') as f:
            await f.write(entry.json(indent=2))

        return {
            "status": "success",
            "entry_id": entry.id,
            "timestamp": datetime.now().isoformat()
        }

    def _matches_query(self, entry: MetadataEntry, query: dict[str, Any]) -> bool:
        """Check if an entry matches search criteria.

        Args:
            entry: Metadata entry to check
            query: Search criteria

        Returns:
            True if entry matches query, False otherwise
        """
        for key, value in query.items():
            if key == "tags":
                if not all(tag in entry.tags for tag in value):
                    return False
            elif key == "name":
                if value.lower() not in entry.name.lower():
                    return False
            elif hasattr(entry, key):
                if getattr(entry, key) != value:
                    return False
        return True
