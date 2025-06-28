"""
Data Transformer Module

This module provides functionality for transforming data between different
formats and structures.
"""

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
import pandas as pd
from pydantic import BaseModel, Field


class TransformationStep(BaseModel):
    """Represents a single transformation step in a pipeline."""
    name: str
    function: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    order: int = 0

class TransformationPipeline(BaseModel):
    """Represents a complete data transformation pipeline."""
    name: str
    description: str
    steps: list[TransformationStep]
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DataTransformer:
    """Class for transforming data between different formats and structures."""

    def __init__(self, pipelines_dir: str = "pipelines"):
        """Initialize the DataTransformer.

        Args:
            pipelines_dir: Directory containing transformation pipelines
        """
        self.pipelines_dir = Path(pipelines_dir)
        self.pipelines_dir.mkdir(parents=True, exist_ok=True)
        self._transformation_functions: dict[str, Callable] = {}

    def register_transformation(
        self,
        name: str,
        function: Callable
    ) -> None:
        """Register a new transformation function.

        Args:
            name: Name of the transformation
            function: Function to perform the transformation
        """
        self._transformation_functions[name] = function

    async def transform(
        self,
        data: dict[str, Any] | pd.DataFrame,
        pipeline_name: str
    ) -> dict[str, Any] | pd.DataFrame:
        """Transform data using a specified pipeline.

        Args:
            data: Data to transform
            pipeline_name: Name of the pipeline to use

        Returns:
            Transformed data
        """
        pipeline = await self.get_pipeline(pipeline_name)

        # Sort steps by order
        steps = sorted(pipeline.steps, key=lambda x: x.order)

        transformed_data = data
        for step in steps:
            if step.function not in self._transformation_functions:
                raise ValueError(f"Unknown transformation function: {step.function}")

            transform_func = self._transformation_functions[step.function]
            transformed_data = transform_func(transformed_data, **step.parameters)

        return transformed_data

    async def create_pipeline(
        self,
        name: str,
        description: str,
        steps: list[TransformationStep]
    ) -> None:
        """Create a new transformation pipeline.

        Args:
            name: Name of the pipeline
            description: Description of the pipeline
            steps: List of transformation steps
        """
        pipeline = TransformationPipeline(
            name=name,
            description=description,
            steps=steps
        )

        pipeline_path = self.pipelines_dir / f"{name}.json"
        async with aiofiles.open(pipeline_path, 'w') as f:
            await f.write(pipeline.json(indent=2))

    async def get_pipeline(self, name: str) -> TransformationPipeline:
        """Get a transformation pipeline definition.

        Args:
            name: Name of the pipeline

        Returns:
            Pipeline definition
        """
        pipeline_path = self.pipelines_dir / f"{name}.json"
        if not pipeline_path.exists():
            raise FileNotFoundError(f"Pipeline not found: {name}")

        async with aiofiles.open(pipeline_path) as f:
            pipeline_data = json.loads(await f.read())
            return TransformationPipeline(**pipeline_data)

    async def list_pipelines(self) -> list[str]:
        """List all available transformation pipelines.

        Returns:
            List of pipeline names
        """
        return [f.stem for f in self.pipelines_dir.glob("*.json")]

    async def update_pipeline(
        self,
        name: str,
        description: str | None = None,
        steps: list[TransformationStep] | None = None
    ) -> None:
        """Update an existing transformation pipeline.

        Args:
            name: Name of the pipeline
            description: New description (optional)
            steps: New list of steps (optional)
        """
        pipeline = await self.get_pipeline(name)

        if description is not None:
            pipeline.description = description
        if steps is not None:
            pipeline.steps = steps

        pipeline.updated_at = datetime.now()

        pipeline_path = self.pipelines_dir / f"{name}.json"
        async with aiofiles.open(pipeline_path, 'w') as f:
            await f.write(pipeline.json(indent=2))
