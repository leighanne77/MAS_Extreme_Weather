"""
Metadata Agent for managing data metadata and schema information.
Handles metadata management, schema validation, and data cataloging.
"""

from datetime import datetime
from typing import Any

from .base_agent import BaseAgent


class MetadataAgent(BaseAgent):
    """Agent responsible for managing data metadata and schema information."""

    def __init__(self):
        super().__init__(
            name="metadata_agent",
            description="Manages data metadata and schema information",
            capabilities={
                "streaming": True,
                "pushNotifications": True,
                "stateTransitionHistory": True
            }
        )
        self.metadata_registry = {}
        self.schema_registry = {}
        self.catalog_entries = {}

    async def manage_metadata(self, data_id: str, metadata: dict[str, Any], action: str = "update") -> dict[str, Any]:
        """Manage data metadata."""
        try:
            if action == "update":
                if data_id not in self.metadata_registry:
                    self.metadata_registry[data_id] = {}

                self.metadata_registry[data_id].update(metadata)
                self.metadata_registry[data_id]["last_updated"] = datetime.utcnow().isoformat()

                return {
                    "status": "success",
                    "message": f"Metadata updated for {data_id}"
                }
            elif action == "delete":
                if data_id in self.metadata_registry:
                    del self.metadata_registry[data_id]

                return {
                    "status": "success",
                    "message": f"Metadata deleted for {data_id}"
                }
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def manage_schema(self, schema_id: str, schema: dict[str, Any], action: str = "update") -> dict[str, Any]:
        """Manage data schema."""
        try:
            if action == "update":
                self.schema_registry[schema_id] = {
                    "schema": schema,
                    "last_updated": datetime.utcnow().isoformat()
                }

                return {
                    "status": "success",
                    "message": f"Schema updated: {schema_id}"
                }
            elif action == "delete":
                if schema_id in self.schema_registry:
                    del self.schema_registry[schema_id]

                return {
                    "status": "success",
                    "message": f"Schema deleted: {schema_id}"
                }
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def catalog_data(self, data_id: str, catalog_info: dict[str, Any]) -> dict[str, Any]:
        """Catalog data with metadata and schema information."""
        try:
            self.catalog_entries[data_id] = {
                "catalog_info": catalog_info,
                "metadata": self.metadata_registry.get(data_id, {}),
                "schema": self.schema_registry.get(catalog_info.get("schema_id")),
                "cataloged_at": datetime.utcnow().isoformat()
            }

            return {
                "status": "success",
                "catalog_entry": self.catalog_entries[data_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_metadata(self, data_id: str) -> dict[str, Any]:
        """Get metadata for data."""
        try:
            if data_id not in self.metadata_registry:
                return {
                    "status": "error",
                    "error": f"No metadata found for {data_id}"
                }

            return {
                "status": "success",
                "metadata": self.metadata_registry[data_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_schema(self, schema_id: str) -> dict[str, Any]:
        """Get schema information."""
        try:
            if schema_id not in self.schema_registry:
                return {
                    "status": "error",
                    "error": f"No schema found for {schema_id}"
                }

            return {
                "status": "success",
                "schema": self.schema_registry[schema_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_catalog_entry(self, data_id: str) -> dict[str, Any]:
        """Get catalog entry for data."""
        try:
            if data_id not in self.catalog_entries:
                return {
                    "status": "error",
                    "error": f"No catalog entry found for {data_id}"
                }

            return {
                "status": "success",
                "catalog_entry": self.catalog_entries[data_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def search_catalog(self, query: dict[str, Any]) -> dict[str, Any]:
        """Search data catalog."""
        try:
            results = []
            for data_id, entry in self.catalog_entries.items():
                if all(entry["catalog_info"].get(k) == v for k, v in query.items()):
                    results.append({
                        "data_id": data_id,
                        "entry": entry
                    })

            return {
                "status": "success",
                "results": results
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
