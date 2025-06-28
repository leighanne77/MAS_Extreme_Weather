"""
Nature-based solutions data source module.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

from .data_source import DataSource

# Configure logging
logger = logging.getLogger(__name__)

class NatureBasedSolutionsSource(DataSource):
    """Data source for nature-based solutions.

    This class provides access to nature-based solutions data for preventing
    damage from extreme weather events.
    """

    def __init__(self):
        """Initialize the nature-based solutions data source."""
        super().__init__()
        self.solutions = []
        self._load_data()

    def _load_data(self):
        """Load nature-based solutions data from JSON file."""
        try:
            data_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(data_dir, "nature_based_solutions.json")

            with open(json_path) as f:
                data = json.load(f)
                self.solutions = data.get("solutions", [])
                logger.info(f"Loaded {len(self.solutions)} nature-based solutions")

        except Exception as e:
            logger.error(f"Error loading nature-based solutions data: {str(e)}")
            self.solutions = []

    async def fetch_data(self, **kwargs) -> dict[str, Any]:
        """Fetch nature-based solutions data.

        Args:
            **kwargs: Additional arguments for fetching data
                - risk_type (str, optional): Filter solutions by risk type
                - location (str, optional): Filter solutions by location type
                - scale (str, optional): Filter solutions by scale (local, city, regional)
                - implementation_level (str, optional): Filter by implementation level

        Returns:
            Dict[str, Any]: Nature-based solutions data
        """
        try:
            self.fetch_count += 1
            self.last_fetch_time = datetime.now()

            # Filter solutions based on kwargs
            filtered_solutions = self.solutions

            if "risk_type" in kwargs:
                risk_type = kwargs["risk_type"].lower()
                filtered_solutions = [
                    s for s in filtered_solutions
                    if risk_type in [r.lower() for r in s.get("risk_types", [])]
                ]

            if "location" in kwargs:
                location = kwargs["location"].lower()
                filtered_solutions = [
                    s for s in filtered_solutions
                    if location in [l.lower() for l in s.get("suitable_locations", [])]
                ]

            if "scale" in kwargs:
                scale = kwargs["scale"].lower()
                filtered_solutions = [
                    s for s in filtered_solutions
                    if s.get("scale", "").lower() == scale
                ]

            if "implementation_level" in kwargs:
                implementation_level = kwargs["implementation_level"].lower()
                filtered_solutions = [
                    s for s in filtered_solutions
                    if s.get("implementation_level", "").lower() == implementation_level
                ]

            return {
                "status": "success",
                "data": filtered_solutions,
                "count": len(filtered_solutions)
            }

        except Exception as e:
            logger.error(f"Error fetching nature-based solutions: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_solution_by_id(self, solution_id: str) -> dict[str, Any]:
        """Get a specific nature-based solution by ID.

        Args:
            solution_id (str): ID of the solution to fetch

        Returns:
            Dict[str, Any]: Solution data if found, error response otherwise
        """
        try:
            solution = next(
                (s for s in self.solutions if s.get("id") == solution_id),
                None
            )

            if solution:
                return {
                    "status": "success",
                    "data": solution
                }
            else:
                return {
                    "status": "error",
                    "error": f"Solution with ID {solution_id} not found"
                }

        except Exception as e:
            logger.error(f"Error getting solution by ID: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_solutions_by_risk_type(self, risk_type: str) -> dict[str, Any]:
        """Get all solutions for a specific risk type.

        Args:
            risk_type (str): Risk type to filter by

        Returns:
            Dict[str, Any]: Solutions for the specified risk type
        """
        return await self.fetch_data(risk_type=risk_type)

    async def get_solutions_by_location(self, location: str) -> dict[str, Any]:
        """Get all solutions suitable for a specific location type.

        Args:
            location (str): Location type to filter by

        Returns:
            Dict[str, Any]: Solutions suitable for the specified location
        """
        return await self.fetch_data(location=location)

    async def get_solutions_by_scale(self, scale: str) -> dict[str, Any]:
        """Get all solutions for a specific scale.

        Args:
            scale (str): Scale to filter by (local, city, regional)

        Returns:
            Dict[str, Any]: Solutions for the specified scale
        """
        return await self.fetch_data(scale=scale)

    async def get_solutions_by_implementation_level(self, implementation_level: str) -> dict[str, Any]:
        """Get all solutions for a specific implementation level.

        Args:
            implementation_level (str): Implementation level to filter by

        Returns:
            Dict[str, Any]: Solutions for the specified implementation level
        """
        return await self.fetch_data(implementation_level=implementation_level)

    async def get_solutions(self,
                          risk_type: str | None = None,
                          location_type: str | None = None,
                          scale: str | None = None,
                          implementation_level: str | None = None) -> dict[str, Any]:
        """Get nature-based solutions with multiple filter options.

        Args:
            risk_type (Optional[str]): Type of risk (e.g., "flooding", "extreme_heat")
            location_type (Optional[str]): Type of location (e.g., "urban", "rural", "coastal")
            scale (Optional[str]): Scale of implementation (e.g., "local", "city", "regional")
            implementation_level (Optional[str]): Implementation level (e.g., "property_owner", "city_regional")

        Returns:
            Dict[str, Any]: Nature-based solutions data
        """
        try:
            # Build filter parameters
            filters = {}
            if risk_type:
                filters["risk_type"] = risk_type
            if location_type:
                filters["location"] = location_type
            if scale:
                filters["scale"] = scale
            if implementation_level:
                filters["implementation_level"] = implementation_level

            return await self.fetch_data(**filters)

        except Exception as e:
            logger.error(f"Error getting nature-based solutions: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_solution_details(self, solution_id: str) -> dict[str, Any]:
        """Get detailed information about a specific solution.

        Args:
            solution_id (str): ID of the solution

        Returns:
            Dict[str, Any]: Detailed solution information
        """
        return await self.get_solution_by_id(solution_id)

    async def get_property_owner_solutions(self) -> dict[str, Any]:
        """Get all solutions that can be implemented by property owners.

        Returns:
            Dict[str, Any]: Property owner implementable solutions
        """
        return await self.get_solutions_by_implementation_level("property_owner")

    async def get_community_solutions(self) -> dict[str, Any]:
        """Get all solutions that can be implemented by communities.

        Returns:
            Dict[str, Any]: Community implementable solutions
        """
        return await self.get_solutions_by_implementation_level("community")

    async def get_city_regional_solutions(self) -> dict[str, Any]:
        """Get all solutions that require city or regional implementation.

        Returns:
            Dict[str, Any]: City/regional implementable solutions
        """
        return await self.get_solutions_by_implementation_level("city_regional")

    async def get_agency_regional_solutions(self) -> dict[str, Any]:
        """Get all solutions that require agency or regional implementation.

        Returns:
            Dict[str, Any]: Agency/regional implementable solutions
        """
        return await self.get_solutions_by_implementation_level("agency_regional")

    def get_all_solutions(self) -> list[dict[str, Any]]:
        """Get all nature-based solutions.

        Returns:
            List[Dict[str, Any]]: All solutions
        """
        return self.solutions

    def get_solution_count(self) -> int:
        """Get the total number of solutions.

        Returns:
            int: Total number of solutions
        """
        return len(self.solutions)

    def get_available_risk_types(self) -> list[str]:
        """Get all available risk types.

        Returns:
            List[str]: All available risk types
        """
        risk_types = set()
        for solution in self.solutions:
            risk_types.update(solution.get("risk_types", []))
        return sorted(risk_types)

    def get_available_scales(self) -> list[str]:
        """Get all available scales.

        Returns:
            List[str]: All available scales
        """
        scales = set()
        for solution in self.solutions:
            scale = solution.get("scale")
            if scale:
                scales.add(scale)
        return sorted(scales)

    def get_available_implementation_levels(self) -> list[str]:
        """Get all available implementation levels.

        Returns:
            List[str]: All available implementation levels
        """
        levels = set()
        for solution in self.solutions:
            level = solution.get("implementation_level")
            if level:
                levels.add(level)
        return sorted(levels)

    def get_metrics(self) -> dict[str, Any]:
        """Get metrics for the data source.

        Returns:
            Dict[str, Any]: Metrics including performance and data statistics
        """
        return {
            "total_solutions": len(self.solutions),
            "available_risk_types": len(self.get_available_risk_types()),
            "available_scales": len(self.get_available_scales()),
            "available_implementation_levels": len(self.get_available_implementation_levels()),
            "last_updated": self.last_fetch_time.isoformat() if hasattr(self, 'last_fetch_time') else None,
            "fetch_count": getattr(self, 'fetch_count', 0)
        }
