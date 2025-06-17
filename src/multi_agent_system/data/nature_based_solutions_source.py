"""
Nature-based solutions data source module.
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime

from .data_source import DataSource

class NatureBasedSolutionsSource(DataSource):
    """Data source for nature-based solutions.
    
    This class provides access to nature-based solutions data for preventing
    damage from extreme weather events.
    """
    
    def __init__(self):
        """Initialize the nature-based solutions data source."""
        super().__init__()
        self._load_data()
        
    def _load_data(self):
        """Load nature-based solutions data from JSON file."""
        try:
            data_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(data_dir, "nature_based_solutions.json")
            
            with open(json_path, 'r') as f:
                self.solutions = json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading nature-based solutions data: {str(e)}")
            self.solutions = []
            
    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """Fetch nature-based solutions data.
        
        Args:
            **kwargs: Additional arguments for fetching data
                - risk_type (str, optional): Filter solutions by risk type
                - location (str, optional): Filter solutions by location type
                
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
                    if risk_type in [r.lower() for r in s["risk_types"]]
                ]
                
            if "location" in kwargs:
                location = kwargs["location"].lower()
                filtered_solutions = [
                    s for s in filtered_solutions
                    if location in [l.lower() for l in s["suitable_locations"]]
                ]
                
            return {
                "status": "success",
                "data": filtered_solutions,
                "count": len(filtered_solutions)
            }
            
        except Exception as e:
            return self.handle_error(e)
            
    async def get_solution_by_id(self, solution_id: str) -> Dict[str, Any]:
        """Get a specific nature-based solution by ID.
        
        Args:
            solution_id (str): ID of the solution to fetch
            
        Returns:
            Dict[str, Any]: Solution data if found, error response otherwise
        """
        try:
            solution = next(
                (s for s in self.solutions if s["id"] == solution_id),
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
            return self.handle_error(e)
            
    async def get_solutions_by_risk_type(self, risk_type: str) -> Dict[str, Any]:
        """Get all solutions for a specific risk type.
        
        Args:
            risk_type (str): Risk type to filter by
            
        Returns:
            Dict[str, Any]: Solutions for the specified risk type
        """
        return await self.fetch_data(risk_type=risk_type)
        
    async def get_solutions_by_location(self, location: str) -> Dict[str, Any]:
        """Get all solutions suitable for a specific location type.
        
        Args:
            location (str): Location type to filter by
            
        Returns:
            Dict[str, Any]: Solutions suitable for the specified location
        """
        return await self.fetch_data(location=location)

    async def get_solutions(self, 
                          risk_type: str,
                          location_type: Optional[str] = None,
                          scale: Optional[str] = None) -> Dict[str, Any]:
        """Get nature-based solutions for a specific risk type.
        
        Args:
            risk_type (str): Type of risk (e.g., "flood_protection", "coastal_protection")
            location_type (Optional[str]): Type of location (e.g., "urban", "rural", "coastal")
            scale (Optional[str]): Scale of implementation (e.g., "small", "medium", "large")
            
        Returns:
            Dict[str, Any]: Nature-based solutions data
        """
        try:
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("get_solutions"):
                # Check circuit breaker
                if not self.circuit_breaker.is_allowed("get_solutions"):
                    raise Exception("Circuit breaker is open for solution retrieval")
                    
                # Get solutions for risk type
                solutions = self.data.get("nature_based_solutions", {}).get(risk_type, {})
                
                # Filter by location type if specified
                if location_type:
                    solutions = {
                        name: solution
                        for name, solution in solutions.items()
                        if location_type in solution["implementation"]["location"]
                    }
                    
                # Filter by scale if specified
                if scale:
                    solutions = {
                        name: solution
                        for name, solution in solutions.items()
                        if scale in solution["implementation"]["scale"]
                    }
                    
                # Update monitoring
                self.monitoring.track_operation("get_solutions", {
                    "risk_type": risk_type,
                    "location_type": location_type,
                    "scale": scale,
                    "solutions_count": len(solutions)
                })
                
                return {
                    "status": "success",
                    "data": solutions,
                    "metadata": self.data.get("nature_based_solutions", {}).get("metadata", {})
                }
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("get_solutions")
            self.logger.error(f"Error getting nature-based solutions: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def get_solution_details(self, risk_type: str, solution_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific solution.
        
        Args:
            risk_type (str): Type of risk
            solution_name (str): Name of the solution
            
        Returns:
            Dict[str, Any]: Detailed solution information
        """
        try:
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("get_solution_details"):
                # Check circuit breaker
                if not self.circuit_breaker.is_allowed("get_solution_details"):
                    raise Exception("Circuit breaker is open for solution details retrieval")
                    
                # Get solution details
                solution = self.data.get("nature_based_solutions", {}).get(risk_type, {}).get(solution_name)
                
                if not solution:
                    raise ValueError(f"Solution {solution_name} not found for risk type {risk_type}")
                    
                # Update monitoring
                self.monitoring.track_operation("get_solution_details", {
                    "risk_type": risk_type,
                    "solution_name": solution_name
                })
                
                return {
                    "status": "success",
                    "data": solution,
                    "metadata": self.data.get("nature_based_solutions", {}).get("metadata", {})
                }
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("get_solution_details")
            self.logger.error(f"Error getting solution details: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get ADK metrics for the data source.
        
        Returns:
            Dict[str, Any]: Metrics including performance, resource usage, and circuit breaker status
        """
        return {
            "performance": self.metrics_collector.get_metrics(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "monitoring": self.monitoring.get_metrics(),
            "last_updated": self.last_updated.isoformat()
        } 