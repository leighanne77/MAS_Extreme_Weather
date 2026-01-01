"""
Data Loader for Tool Multi-Agent System

This module provides utilities to load and access all data files used by the system.
Note: Opportunity Zone API, NOAA NCEI/ENOW, and USGS TWL API integrations are available via data_loader.py methods. See documentation for usage and agent integration.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from . import opportunity_zone_api
import logging
import requests

# NOAA NCEI and ENOW API endpoints
NCEI_DATA_SERVICE_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
ENOW_API_URL = "https://coast.noaa.gov/api/enow/"
USGS_TWL_API_URL = "https://coastal.er.usgs.gov/hurricanes/research/twlviewer/api/"

class DataLoader:
    """Load and manage data files for the Tool system."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the data loader."""
        if data_dir is None:
            # Default to the data directory relative to this file
            self.data_dir = Path(__file__).parent
        else:
            self.data_dir = Path(data_dir)
        
        self._cache = {}
    
    def load_nature_based_solutions(self) -> Dict[str, Any]:
        """Load nature-based solutions data."""
        cache_key = "nature_based_solutions"
        if cache_key not in self._cache:
            file_path = self.data_dir / "nature_based_solutions.json"
            with open(file_path, 'r') as f:
                self._cache[cache_key] = json.load(f)
        return self._cache[cache_key]
    
    def load_historical_weather_events(self) -> Dict[str, Any]:
        """Load historical weather events data."""
        cache_key = "historical_weather_events"
        if cache_key not in self._cache:
            file_path = self.data_dir / "historical_weather_events.json"
            with open(file_path, 'r') as f:
                self._cache[cache_key] = json.load(f)
        return self._cache[cache_key]
    
    def load_economic_impact_data(self) -> Dict[str, Any]:
        """Load economic impact data."""
        cache_key = "economic_impact_data"
        if cache_key not in self._cache:
            file_path = self.data_dir / "economic_impact_data.json"
            with open(file_path, 'r') as f:
                self._cache[cache_key] = json.load(f)
        return self._cache[cache_key]
    
    def load_regional_risk_profiles(self) -> Dict[str, Any]:
        """Load regional risk profiles data."""
        cache_key = "regional_risk_profiles"
        if cache_key not in self._cache:
            file_path = self.data_dir / "regional_risk_profiles.json"
            with open(file_path, 'r') as f:
                self._cache[cache_key] = json.load(f)
        return self._cache[cache_key]
    
    def load_static_opportunity_zones(self, static_path: str = None) -> List[dict]:
        """Load static Opportunity Zone data from JSON file."""
        cache_key = "static_opportunity_zones"
        if cache_key not in self._cache:
            if static_path is None:
                file_path = self.data_dir / "opportunity_zones.json"
            else:
                file_path = Path(static_path)
            with open(file_path, 'r') as f:
                self._cache[cache_key] = json.load(f)
        return self._cache[cache_key]

    def get_opportunity_zones(self, source: str = "static", **kwargs) -> List[dict]:
        """
        Unified interface to get Opportunity Zone data.
        Args:
            source (str): 'static' for local JSON, 'api' for live HUD API.
            kwargs: Arguments for filtering/querying (see below).
        Returns:
            List[dict]: List of Opportunity Zone features.
        Usage:
            get_opportunity_zones(source="static")
            get_opportunity_zones(source="api", state_abbr="AL")
            get_opportunity_zones(source="api", county_fips="01097", min_area=1000000)
        """
        if source == "static":
            return self.load_static_opportunity_zones()
        elif source == "api":
            return opportunity_zone_api.get_opportunity_zones_custom(**kwargs)
        else:
            raise ValueError(f"Unknown OZ data source: {source}")

    def get_opportunity_zone_by_tract(self, tract_id: str, source: str = "static") -> dict:
        """
        Get a single Opportunity Zone by tract GEOID from static or live data.
        Args:
            tract_id (str): Census Tract GEOID
            source (str): 'static' or 'api'
        Returns:
            dict or None: OZ feature dict or None if not found
        """
        if source == "static":
            ozs = self.load_static_opportunity_zones()
            for oz in ozs:
                if oz.get("TRACTCE10") == tract_id:
                    return oz
            return None
        elif source == "api":
            return opportunity_zone_api.get_opportunity_zone_by_tract(tract_id)
        else:
            raise ValueError(f"Unknown OZ data source: {source}")

    def get_solution_by_id(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific nature-based solution by ID."""
        data = self.load_nature_based_solutions()
        for solution in data.get("solutions", []):
            if solution.get("id") == solution_id:
                return solution
        return None
    
    def get_solutions_by_risk_type(self, risk_type: str) -> List[Dict[str, Any]]:
        """Get nature-based solutions that address a specific risk type."""
        data = self.load_nature_based_solutions()
        solutions = []
        for solution in data.get("solutions", []):
            if risk_type in solution.get("risk_types", []):
                solutions.append(solution)
        return solutions
    
    def get_solutions_by_location(self, location_type: str) -> List[Dict[str, Any]]:
        """Get nature-based solutions suitable for a specific location type."""
        data = self.load_nature_based_solutions()
        solutions = []
        for solution in data.get("solutions", []):
            if location_type in solution.get("suitable_locations", []):
                solutions.append(solution)
        return solutions
    
    def get_historical_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific historical weather event by ID."""
        data = self.load_historical_weather_events()
        for event in data.get("events", []):
            if event.get("id") == event_id:
                return event
        return None
    
    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get historical weather events of a specific type."""
        data = self.load_historical_weather_events()
        events = []
        for event in data.get("events", []):
            if event.get("type") == event_type:
                events.append(event)
        return events
    
    def get_events_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Get historical weather events in a specific region."""
        data = self.load_historical_weather_events()
        events = []
        for event in data.get("events", []):
            location = event.get("location", {})
            if region.lower() in location.get("region", "").lower():
                events.append(event)
        return events
    
    def get_regional_profile(self, region_name: str) -> Optional[Dict[str, Any]]:
        """Get risk profile for a specific region."""
        data = self.load_regional_risk_profiles()
        return data.get("regions", {}).get(region_name)
    
    def get_economic_impact_by_event_type(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get economic impact data for a specific event type."""
        data = self.load_economic_impact_data()
        impacts = data.get("economic_impacts", {})
        
        if event_type == "hurricane":
            return impacts.get("hurricane_impacts")
        elif event_type == "drought":
            return impacts.get("drought_impacts")
        elif event_type == "flood":
            return impacts.get("flood_impacts")
        elif event_type == "heat_wave":
            return impacts.get("heat_wave_impacts")
        
        return None
    
    def get_adaptation_cost_benefits(self, solution_type: str = None) -> Dict[str, Any]:
        """Get adaptation cost-benefit data."""
        data = self.load_economic_impact_data()
        cost_benefits = data.get("adaptation_cost_benefits", {})
        
        if solution_type:
            return cost_benefits.get(solution_type, {})
        
        return cost_benefits
    
    def get_insurance_impacts(self) -> Dict[str, Any]:
        """Get insurance impact data."""
        data = self.load_economic_impact_data()
        return data.get("insurance_impacts", {})
    
    def get_investment_returns(self) -> Dict[str, Any]:
        """Get investment return data."""
        data = self.load_economic_impact_data()
        return data.get("investment_returns", {})
    
    def get_regional_variations(self) -> Dict[str, Any]:
        """Get regional variation data."""
        data = self.load_economic_impact_data()
        return data.get("regional_variations", {})
    
    def search_solutions(self, query: str) -> List[Dict[str, Any]]:
        """Search nature-based solutions by query."""
        data = self.load_nature_based_solutions()
        solutions = []
        query_lower = query.lower()
        
        for solution in data.get("solutions", []):
            # Search in name, description, and benefits
            if (query_lower in solution.get("name", "").lower() or
                query_lower in solution.get("description", "").lower() or
                any(query_lower in benefit.lower() for benefit in solution.get("benefits", []))):
                solutions.append(solution)
        
        return solutions
    
    def get_all_data_summary(self) -> Dict[str, Any]:
        """Get a summary of all available data."""
        summary = {
            "nature_based_solutions": {
                "count": len(self.load_nature_based_solutions().get("solutions", [])),
                "risk_types": set(),
                "location_types": set()
            },
            "historical_events": {
                "count": len(self.load_historical_weather_events().get("events", [])),
                "event_types": set(),
                "regions": set()
            },
            "regions": {
                "count": len(self.load_regional_risk_profiles().get("regions", {})),
                "region_names": list(self.load_regional_risk_profiles().get("regions", {}).keys())
            }
        }
        
        # Collect unique values
        for solution in self.load_nature_based_solutions().get("solutions", []):
            summary["nature_based_solutions"]["risk_types"].update(solution.get("risk_types", []))
            summary["nature_based_solutions"]["location_types"].update(solution.get("suitable_locations", []))
        
        for event in self.load_historical_weather_events().get("events", []):
            summary["historical_events"]["event_types"].add(event.get("type"))
            summary["historical_events"]["regions"].add(event.get("location", {}).get("region"))
        
        # Convert sets to lists for JSON serialization
        summary["nature_based_solutions"]["risk_types"] = list(summary["nature_based_solutions"]["risk_types"])
        summary["nature_based_solutions"]["location_types"] = list(summary["nature_based_solutions"]["location_types"])
        summary["historical_events"]["event_types"] = list(summary["historical_events"]["event_types"])
        summary["historical_events"]["regions"] = list(summary["historical_events"]["regions"])
        
        return summary
    
    def get_solution_biodiversity_impact(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """Get biodiversity impact data for a specific nature-based solution."""
        solution = self.get_solution_by_id(solution_id)
        if solution:
            return solution.get("biodiversity_impact")
        return None
    
    def get_regional_biodiversity_risks(self, region_name: str) -> Optional[Dict[str, Any]]:
        """Get biodiversity risk data for a specific region."""
        region_data = self.get_regional_profile(region_name)
        if region_data:
            return region_data.get("biodiversity_risks")
        return None
    
    def get_ecosystem_service_values(self) -> Dict[str, Any]:
        """Get ecosystem service value data from economic impact data."""
        data = self.load_economic_impact_data()
        return data.get("biodiversity_impacts", {}).get("ecosystem_service_value", {})
    
    def get_solutions_by_biodiversity_benefit(self, benefit_type: str) -> List[Dict[str, Any]]:
        """Get solutions that provide specific biodiversity benefits."""
        data = self.load_nature_based_solutions()
        solutions = []
        
        for solution in data.get("solutions", []):
            biodiversity_impact = solution.get("biodiversity_impact", {})
            if benefit_type in biodiversity_impact.get("benefits", []):
                solutions.append(solution)
        
        return solutions
    
    def get_conservation_compliance_costs(self) -> Dict[str, Any]:
        """Get conservation compliance cost data."""
        data = self.load_economic_impact_data()
        return data.get("biodiversity_impacts", {}).get("conservation_compliance", {})

    def get_noaa_ncei_coastal_erosion(self, dataset: str, start_date: str, end_date: str, bbox: str, data_types: str = None, units: str = "metric", format: str = "json") -> list:
        """
        Fetch coastal erosion or related data from NOAA NCEI Access Data Service API.
        Args:
            dataset (str): NCEI dataset name (e.g., 'global-hourly', 'daily-summaries')
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            bbox (str): Bounding box ("minLon,minLat,maxLon,maxLat")
            data_types (str): Comma-separated data types (optional)
            units (str): 'metric' or 'standard'
            format (str): 'json', 'csv', etc.
        Returns:
            list: List of data records (dicts)
        """
        params = {
            "dataset": dataset,
            "startDate": start_date,
            "endDate": end_date,
            "bbox": bbox,
            "units": units,
            "format": format
        }
        if data_types:
            params["dataTypes"] = data_types
        try:
            resp = requests.get(NCEI_DATA_SERVICE_URL, params=params, timeout=20)
            resp.raise_for_status()
            return resp.json() if format == "json" else resp.text
        except Exception as e:
            logging.error(f"NCEI API error: {e}", exc_info=True)
            return []

    def get_noaa_enow_data(self, region_type: str, region_id: str, sector: str = None, year: int = None) -> dict:
        """
        Fetch ENOW (Economics: National Ocean Watch) data from NOAA Digital Coast API.
        Args:
            region_type (str): 'state', 'county', or 'metro'
            region_id (str): FIPS code or region code
            sector (str): ENOW sector (optional, e.g., 'total', 'living_resources', etc.)
            year (int): Year (optional)
        Returns:
            dict: ENOW data response
        """
        url = f"{ENOW_API_URL}{region_type}/{region_id}"
        params = {}
        if sector:
            params["sector"] = sector
        if year:
            params["year"] = year
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logging.error(f"ENOW API error: {e}", exc_info=True)
            return {}

    def get_usgs_twl_data(self, site: str = None, start: str = None, end: str = None, event: str = None) -> dict:
        """
        Fetch Total Water Level (TWL) data from USGS TWL Viewer API.
        Args:
            site (str): Site code (optional, e.g., 'AL001')
            start (str): Start date (YYYY-MM-DD, optional)
            end (str): End date (YYYY-MM-DD, optional)
            event (str): Event name (optional, e.g., 'Sally2020')
        Returns:
            dict: TWL data response
        """
        params = {}
        if site:
            params["site"] = site
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if event:
            params["event"] = event
        try:
            resp = requests.get(USGS_TWL_API_URL, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logging.error(f"USGS TWL API error: {e}", exc_info=True)
            return {}

    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()

# Global instance for easy access
data_loader = DataLoader()

def get_data_loader() -> DataLoader:
    """Get the global data loader instance."""
    return data_loader