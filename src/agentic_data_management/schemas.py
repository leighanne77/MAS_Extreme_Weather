"""
Schema Manager Module

This module provides functionality for managing data schemas and their versions.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel, Field


class SchemaVersion(BaseModel):
    """Represents a version of a data schema."""
    version: str
    schema: dict[str, Any]
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    is_active: bool = True

class Schema(BaseModel):
    """Represents a complete data schema with version history."""
    name: str
    description: str
    versions: list[SchemaVersion]
    current_version: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class SchemaManager:
    """Class for managing data schemas and their versions."""

    def __init__(self, schemas_dir: str = "schemas"):
        """Initialize the SchemaManager.

        Args:
            schemas_dir: Directory containing schema definitions
        """
        self.schemas_dir = Path(schemas_dir)
        self.schemas_dir.mkdir(parents=True, exist_ok=True)

    async def create_schema(
        self,
        name: str,
        description: str,
        initial_schema: dict[str, Any],
        created_by: str
    ) -> None:
        """Create a new schema with an initial version.

        Args:
            name: Name of the schema
            description: Description of the schema
            initial_schema: Initial schema definition
            created_by: User creating the schema
        """
        version = SchemaVersion(
            version="1.0.0",
            schema=initial_schema,
            description="Initial version",
            created_by=created_by
        )

        schema = Schema(
            name=name,
            description=description,
            versions=[version],
            current_version="1.0.0"
        )

        schema_path = self.schemas_dir / f"{name}.json"
        async with aiofiles.open(schema_path, 'w') as f:
            await f.write(schema.json(indent=2))

    async def add_version(
        self,
        name: str,
        schema: dict[str, Any],
        description: str,
        created_by: str,
        version: str | None = None
    ) -> None:
        """Add a new version to an existing schema.

        Args:
            name: Name of the schema
            schema: New schema definition
            description: Description of the new version
            created_by: User creating the version
            version: Optional version string (auto-generated if not provided)
        """
        schema_obj = await self.get_schema(name)

        # Generate version if not provided
        if version is None:
            current_version = schema_obj.current_version
            major, minor, patch = map(int, current_version.split('.'))
            version = f"{major}.{minor}.{patch + 1}"

        new_version = SchemaVersion(
            version=version,
            schema=schema,
            description=description,
            created_by=created_by
        )

        schema_obj.versions.append(new_version)
        schema_obj.current_version = version
        schema_obj.updated_at = datetime.now()

        schema_path = self.schemas_dir / f"{name}.json"
        async with aiofiles.open(schema_path, 'w') as f:
            await f.write(schema_obj.json(indent=2))

    async def get_schema(self, name: str) -> Schema:
        """Get a schema definition.

        Args:
            name: Name of the schema

        Returns:
            Schema definition
        """
        schema_path = self.schemas_dir / f"{name}.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {name}")

        async with aiofiles.open(schema_path) as f:
            schema_data = json.loads(await f.read())
            return Schema(**schema_data)

    async def get_version(
        self,
        name: str,
        version: str | None = None
    ) -> SchemaVersion:
        """Get a specific version of a schema.

        Args:
            name: Name of the schema
            version: Version to get (uses current version if not provided)

        Returns:
            Schema version definition
        """
        schema = await self.get_schema(name)

        if version is None:
            version = schema.current_version

        for schema_version in schema.versions:
            if schema_version.version == version:
                return schema_version

        raise ValueError(f"Version {version} not found in schema {name}")

    async def list_schemas(self) -> list[str]:
        """List all available schemas.

        Returns:
            List of schema names
        """
        return [f.stem for f in self.schemas_dir.glob("*.json")]

    async def list_versions(self, name: str) -> list[str]:
        """List all versions of a schema.

        Args:
            name: Name of the schema

        Returns:
            List of version strings
        """
        schema = await self.get_schema(name)
        return [v.version for v in schema.versions]

    async def set_active_version(
        self,
        name: str,
        version: str
    ) -> None:
        """Set the active version of a schema.

        Args:
            name: Name of the schema
            version: Version to set as active
        """
        schema = await self.get_schema(name)

        # Verify version exists
        version_exists = any(v.version == version for v in schema.versions)
        if not version_exists:
            raise ValueError(f"Version {version} not found in schema {name}")

        schema.current_version = version
        schema.updated_at = datetime.now()

        schema_path = self.schemas_dir / f"{name}.json"
        async with aiofiles.open(schema_path, 'w') as f:
            await f.write(schema.json(indent=2))
