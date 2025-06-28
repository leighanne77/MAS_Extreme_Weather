"""
Data Manager Module

This module provides the core functionality for managing data operations
in the Agentic Data Management System.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel, Field

from .governance import DataGovernance
from .quality import QualityMetrics
from .schemas import SchemaManager
from .transformers import DataTransformer
from .validators import DataValidator


class DataOperation(BaseModel):
    """Represents a data operation with metadata."""
    operation_id: str
    timestamp: datetime
    operation_type: str
    data_source: str
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class DataManager:
    """Main class for managing data operations."""

    def __init__(
        self,
        data_dir: str = "data",
        schema_dir: str = "schemas",
        cache_dir: str = "cache"
    ):
        """Initialize the DataManager.

        Args:
            data_dir: Directory for storing data files
            schema_dir: Directory for storing schema definitions
            cache_dir: Directory for caching processed data
        """
        self.data_dir = Path(data_dir)
        self.schema_dir = Path(schema_dir)
        self.cache_dir = Path(cache_dir)

        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.schema_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.schema_manager = SchemaManager(schema_dir)
        self.quality_metrics = QualityMetrics()
        self.governance = DataGovernance()

        # Operation tracking
        self._operation_lock = asyncio.Lock()
        self._operations: dict[str, DataOperation] = {}

    async def process_data(
        self,
        data_source: str,
        validation_rules: str,
        transformation_pipeline: str,
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Process and validate data.

        Args:
            data_source: Source of the data
            validation_rules: Rules to validate against
            transformation_pipeline: Pipeline to transform data
            metadata: Additional metadata

        Returns:
            Dict containing processing results
        """
        operation = DataOperation(
            operation_id=f"op_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            operation_type="process",
            data_source=data_source,
            status="started",
            metadata=metadata or {}
        )

        async with self._operation_lock:
            self._operations[operation.operation_id] = operation

        try:
            # Load and validate schema
            schema = await self.schema_manager.get_schema(validation_rules)

            # Load data
            data = await self._load_data(data_source)

            # Validate data
            validation_result = await self.validator.validate(data, schema)
            if not validation_result["valid"]:
                raise ValueError(f"Data validation failed: {validation_result['errors']}")

            # Transform data
            transformed_data = await self.transformer.transform(
                data,
                transformation_pipeline
            )

            # Calculate quality metrics
            metrics = await self.quality_metrics.calculate(transformed_data)

            # Update operation status
            operation.status = "completed"
            operation.metadata.update({
                "validation_result": validation_result,
                "quality_metrics": metrics
            })

            return {
                "operation_id": operation.operation_id,
                "status": "success",
                "data": transformed_data,
                "metrics": metrics
            }

        except Exception as e:
            operation.status = "failed"
            operation.metadata["error"] = str(e)
            raise

    async def get_quality_metrics(
        self,
        data_source: str,
        time_range: dict[str, datetime] | None = None
    ) -> dict[str, Any]:
        """Get quality metrics for a data source.

        Args:
            data_source: Source of the data
            time_range: Optional time range to filter metrics

        Returns:
            Dict containing quality metrics
        """
        return await self.quality_metrics.get_metrics(
            data_source,
            time_range
        )

    async def _load_data(self, data_source: str) -> dict[str, Any]:
        """Load data from source.

        Args:
            data_source: Source of the data

        Returns:
            Loaded data
        """
        data_path = self.data_dir / f"{data_source}.json"
        if not data_path.exists():
            raise FileNotFoundError(f"Data source not found: {data_source}")

        async with aiofiles.open(data_path) as f:
            return json.loads(await f.read())

    async def save_data(
        self,
        data: dict[str, Any],
        data_source: str,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """Save data to storage.

        Args:
            data: Data to save
            data_source: Target data source
            metadata: Additional metadata

        Returns:
            Operation ID
        """
        operation = DataOperation(
            operation_id=f"op_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            operation_type="save",
            data_source=data_source,
            status="started",
            metadata=metadata or {}
        )

        async with self._operation_lock:
            self._operations[operation.operation_id] = operation

        try:
            data_path = self.data_dir / f"{data_source}.json"
            async with aiofiles.open(data_path, 'w') as f:
                await f.write(json.dumps(data, indent=2))

            operation.status = "completed"
            return operation.operation_id

        except Exception as e:
            operation.status = "failed"
            operation.metadata["error"] = str(e)
            raise
