"""
Data Lineage Agent Module

This module provides an agent for tracking and managing data lineage.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles

from .base_agent import BaseAgent


class LineageNode(BaseModel):
    """Represents a node in the data lineage graph."""
    id: str
    type: str  # dataset, transformation, source, etc.
    name: str
    metadata: dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class LineageEdge(BaseModel):
    """Represents an edge in the data lineage graph."""
    source_id: str
    target_id: str
    type: str  # reads, writes, transforms, etc.
    metadata: dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)

class LineageGraph(BaseModel):
    """Represents a complete data lineage graph."""
    nodes: list[LineageNode] = []
    edges: list[LineageEdge] = []
    metadata: dict[str, Any] = {}

class LineageAgent(BaseAgent):
    """Agent responsible for tracking and managing data lineage."""

    def __init__(
        self,
        agent_id: str,
        lineage_dir: str = "lineage",
        config: dict[str, Any] | None = None
    ):
        """Initialize the lineage agent.

        Args:
            agent_id: Unique identifier for the agent
            lineage_dir: Directory for storing lineage data
            config: Optional configuration dictionary
        """
        super().__init__(agent_id, config)
        self.lineage_dir = Path(lineage_dir)
        self.lineage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"lineage_agent.{agent_id}")

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute lineage operations.

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

            if operation == "track":
                result = await self._track_lineage(context)
            elif operation == "query":
                result = await self._query_lineage(context)
            elif operation == "update":
                result = await self._update_lineage(context)
            else:
                raise ValueError(f"Unknown operation: {operation}")

            await self.update_state("completed")
            return result

        except Exception as e:
            await self.handle_error(e)
            raise

    async def _track_lineage(self, context: dict[str, Any]) -> dict[str, Any]:
        """Track new lineage information.

        Args:
            context: Context containing lineage information

        Returns:
            Tracking result
        """
        nodes = context.get("nodes", [])
        edges = context.get("edges", [])

        if not nodes and not edges:
            raise ValueError("No lineage information provided")

        # Create lineage graph
        graph = LineageGraph(
            nodes=[LineageNode(**node) for node in nodes],
            edges=[LineageEdge(**edge) for edge in edges],
            metadata=context.get("metadata", {})
        )

        # Save lineage graph
        graph_path = self.lineage_dir / f"lineage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        async with aiofiles.open(graph_path, 'w') as f:
            await f.write(graph.json(indent=2))

        return {
            "status": "success",
            "graph_id": graph_path.stem,
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "timestamp": datetime.now().isoformat()
        }

    async def _query_lineage(
        self,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Query lineage information.

        Args:
            context: Context containing query parameters

        Returns:
            Query results
        """
        query = context.get("query", {})
        results = []

        # Search through lineage graphs
        for graph_path in self.lineage_dir.glob("lineage_*.json"):
            async with aiofiles.open(graph_path) as f:
                graph_data = json.loads(await f.read())
                graph = LineageGraph(**graph_data)

                # Apply query filters
                if self._matches_query(graph, query):
                    results.append(graph.dict())

        return {
            "status": "success",
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }

    async def _update_lineage(self, context: dict[str, Any]) -> dict[str, Any]:
        """Update existing lineage information.

        Args:
            context: Context containing update information

        Returns:
            Update result
        """
        graph_id = context.get("graph_id")
        if not graph_id:
            raise ValueError("No graph_id provided in context")

        updates = context.get("updates", {})
        if not updates:
            raise ValueError("No updates provided in context")

        # Load existing graph
        graph_path = self.lineage_dir / f"{graph_id}.json"
        if not graph_path.exists():
            raise ValueError(f"Lineage graph not found: {graph_id}")

        async with aiofiles.open(graph_path) as f:
            graph_data = json.loads(await f.read())
            graph = LineageGraph(**graph_data)

        # Apply updates
        if "nodes" in updates:
            graph.nodes = [LineageNode(**node) for node in updates["nodes"]]
        if "edges" in updates:
            graph.edges = [LineageEdge(**edge) for edge in updates["edges"]]
        if "metadata" in updates:
            graph.metadata.update(updates["metadata"])

        # Save updated graph
        async with aiofiles.open(graph_path, 'w') as f:
            await f.write(graph.json(indent=2))

        return {
            "status": "success",
            "graph_id": graph_id,
            "timestamp": datetime.now().isoformat()
        }

    def _matches_query(self, graph: LineageGraph, query: dict[str, Any]) -> bool:
        """Check if a graph matches query criteria.

        Args:
            graph: Lineage graph to check
            query: Query criteria

        Returns:
            True if graph matches query, False otherwise
        """
        for key, value in query.items():
            if key == "node_type":
                if not any(node.type == value for node in graph.nodes):
                    return False
            elif key == "edge_type":
                if not any(edge.type == value for edge in graph.edges):
                    return False
            elif key in graph.metadata:
                if graph.metadata[key] != value:
                    return False
        return True
