"""
Enhanced Data Sources for Multi-Agent System

This module implements additional data sources that agents can use
to provide more comprehensive analysis for each prototype.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import requests

from ..utils.geography_parser import GeographicContext, GeographyParser, parse_location
from .data_source import DataSource
from .data_enums import DataLoadStatus, ProvenanceType, DataSourceType

logger = logging.getLogger(__name__)

class EnhancedDataSource(DataSource):
    """Base class for enhanced data sources with caching and error handling."""

    def __init__(self, cache_dir: str = ".cache"):
        super().__init__()
        self.cache_dir = Path(cache_dir) / self.__class__.__name__.lower()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = timedelta(hours=6)  # 6-hour cache for external data

    def _get_cache_key(self, params: dict) -> str:
        """Generate cache key from parameters."""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{cache_key}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is still valid."""
        if not cache_path.exists():
            return False
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age < self.cache_expiry

    def _save_to_cache(self, data: dict, cache_path: Path):
        """Save data to cache."""
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, default=str)
        except Exception as e:
            logger.warning(f"Failed to save to cache: {e}")

    def _load_from_cache(self, cache_path: Path) -> dict | None:
        """Load data from cache."""
        try:
            with open(cache_path) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
            return None

class USDAWaterData(EnhancedDataSource):
    """USDA water-related data sources."""

    def __init__(self, api_key: str | None = None):
        super().__init__()
        self.api_key = api_key
        self.base_urls = {
            "drought_monitor": "https://droughtmonitor.unl.edu/data/json",
            "crop_water": "https://quickstats.nass.usda.gov/api",
            "soil_survey": "https://SDMDataAccess.sc.egov.usda.gov/Tabular/SDMTabularService.asmx"
        }

    async def fetch_data(self, **kwargs) -> dict[str, Any]:
        """Fetch data from USDA water sources."""
        try:
            location = kwargs.get("location", "")
            data_type = kwargs.get("data_type", "drought")
            
            if data_type == "drought":
                return await self.get_drought_data(location)
            elif data_type == "crop_water":
                crop = kwargs.get("crop", "corn")
                return await self.get_crop_water_requirements(crop, location)
            else:
                return {"status": DataLoadStatus.ERROR, "error": f"Unknown data type: {data_type}"}
                
        except Exception as e:
            return {"status": DataLoadStatus.ERROR, "error": str(e)}

    async def get_drought_data(self, state: str, county: str = None) -> dict[str, Any]:
        """Get drought monitor data."""
        try:
            params = {"state": state}
            if county:
                params["county"] = county

            cache_key = self._get_cache_key(params)
            cache_path = self._get_cache_path(cache_key)

            if self._is_cache_valid(cache_path):
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    return {"status": DataLoadStatus.SUCCESS, "data": cached_data, "source": "cache", "provenance": ProvenanceType.STATIC}

            response = requests.get(f"{self.base_urls['drought_monitor']}/current", params=params)
            response.raise_for_status()
            data = response.json()

            self._save_to_cache(data, cache_path)
            return {"status": DataLoadStatus.SUCCESS, "data": data, "source": "api", "provenance": ProvenanceType.API}

        except Exception as e:
            logger.error(f"Error fetching drought data: {e}")
            return {"status": DataLoadStatus.ERROR, "error": str(e)}

    async def get_crop_water_requirements(self, crop: str, state: str) -> dict[str, Any]:
        """Get crop water requirement data."""
        try:
            params = {
                "commodity_desc": crop,
                "state_alpha": state,
                "format": "JSON"
            }

            cache_key = self._get_cache_key(params)
            cache_path = self._get_cache_path(cache_key)

            if self._is_cache_valid(cache_path):
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    return {"status": DataLoadStatus.SUCCESS, "data": cached_data, "source": "cache", "provenance": ProvenanceType.STATIC}

            response = requests.get(f"{self.base_urls['crop_water']}/api_GET", params=params)
            response.raise_for_status()
            data = response.json()

            self._save_to_cache(data, cache_path)
            return {"status": DataLoadStatus.SUCCESS, "data": data, "source": "api", "provenance": ProvenanceType.API}

        except Exception as e:
            logger.error(f"Error fetching crop water data: {e}")
            return {"status": DataLoadStatus.ERROR, "error": str(e)}

class StateAgencyData(EnhancedDataSource):
    """
    State-level agency data sources.
    
    Supports US and India administrative hierarchies.
    Provides decision support data only - results are for user review.
    """

    def __init__(self, state: str = None, location: str = None):
        """
        Initialize state agency data source.
        
        Args:
            state: State name (for backward compatibility)
            location: Location string (e.g., "Mobile Bay, Alabama" or "Chennai, Tamil Nadu, India")
        """
        super().__init__()
        self.geography_parser = GeographyParser()
        
        if location:
            # Parse location to get state and country
            self.geographic_context = self.geography_parser.parse_location(location)
            self.state = self.geographic_context.state_province.lower() if self.geographic_context.state_province else None
            self.country = self.geographic_context.country
        elif state:
            # Backward compatibility: use state directly
            self.state = state.lower()
            self.country = "us"  # Default to US for backward compatibility
            self.geographic_context = None
        else:
            raise ValueError("Either 'state' or 'location' must be provided")
        
        self.agencies = self._get_state_agencies()

    def _get_state_agencies(self) -> dict[str, str]:
        """
        Get state-specific agency URLs.
        
        Supports US and India administrative hierarchies.
        """
        # US State Agencies
        us_agencies = {
            "kansas": {
                "water_office": "https://www.kwo.ks.gov",
                "geological_survey": "https://www.kgs.ku.edu",
                "agriculture": "https://agriculture.ks.gov",
                "environment": "https://www.kdhe.ks.gov"
            },
            "florida": {
                "environmental_protection": "https://floridadep.gov",
                "agriculture": "https://www.fdacs.gov",
                "economic_opportunity": "https://floridajobs.org",
                "emergency_management": "https://www.floridadisaster.org"
            },
            "north_carolina": {
                "environmental_quality": "https://deq.nc.gov",
                "agriculture": "https://www.ncagr.gov",
                "commerce": "https://www.nccommerce.com",
                "emergency_management": "https://www.ncdps.gov"
            },
            "alabama": {
                "environmental_management": "https://adem.alabama.gov",
                "agriculture": "https://agi.alabama.gov",
                "commerce": "https://www.madeinalabama.com",
                "emergency_management": "https://ema.alabama.gov"
            }
        }
        
        # India State Agencies (sample - can be expanded)
        india_agencies = {
            "tamil nadu": {
                "environment": "https://www.tnenvis.nic.in",
                "agriculture": "https://www.tnagri.gov.in",
                "commerce": "https://www.tn.gov.in",
                "disaster_management": "https://www.tn.gov.in"
            },
            "maharashtra": {
                "environment": "https://www.mpcb.gov.in",
                "agriculture": "https://www.mahaagri.gov.in",
                "commerce": "https://www.maharashtra.gov.in",
                "disaster_management": "https://www.maharashtra.gov.in"
            }
        }
        
        if self.country == "india" and self.state:
            # Normalize state name for India
            state_normalized = self.state.lower()
            # Handle Tamil Nadu specifically
            if "tamil" in state_normalized and "nadu" in state_normalized:
                state_normalized = "tamil nadu"
            return india_agencies.get(state_normalized, {})
        elif self.country == "us" and self.state:
            return us_agencies.get(self.state, {})
        else:
            return {}

    async def fetch_data(self, **kwargs) -> dict[str, Any]:
        """Fetch state agency data."""
        try:
            data_type = kwargs.get("data_type", "water")
            
            if data_type == "water":
                return await self.get_water_data()
            elif data_type == "agricultural":
                return await self.get_agricultural_data()
            else:
                return {"status": "error", "error": f"Unknown data type: {data_type}"}
                
        except Exception as e:
            return self.handle_error(e)

    async def get_water_data(self) -> dict[str, Any]:
        """Get state water management data."""
        try:
            if "water_office" in self.agencies:
                # Simulate API call to state water office
                data = {
                    "state": self.state,
                    "water_allocation": "current_allocations",
                    "management_plans": "water_management_strategies",
                    "monitoring_data": "water_quality_metrics"
                }
                return {"status": "success", "data": data}
            else:
                return {"status": "error", "error": f"No water agency data for {self.state}"}

        except Exception as e:
            logger.error(f"Error fetching state water data: {e}")
            return {"status": "error", "error": str(e)}

    async def get_agricultural_data(self) -> dict[str, Any]:
        """Get state agricultural data."""
        try:
            if "agriculture" in self.agencies:
                # Simulate API call to state agriculture department
                data = {
                    "state": self.state,
                    "crop_statistics": "production_data",
                    "market_information": "price_data",
                    "extension_services": "research_data"
                }
                return {"status": "success", "data": data}
            else:
                return {"status": "error", "error": f"No agriculture agency data for {self.state}"}

        except Exception as e:
            logger.error(f"Error fetching state agricultural data: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_state_environmental_data(self, state: str) -> dict[str, Any]:
        """
        Get state environmental data.
        
        NOTE: This is a decision support tool. Results are reference examples for user review only.
        Users must review all recommendations - this is NOT automated decision-making.
        
        Args:
            state: State name (e.g., "Alabama", "Tamil Nadu")
        
        Returns:
            Dict containing environmental data for the state
        """
        try:
            # Parse state to get country context
            location_str = f"{state}, {self.country.upper()}" if self.country else state
            context = self.geography_parser.parse_location(location_str)
            
            state_lower = context.state_province.lower() if context.state_province else state.lower()
            
            # Get agencies for this state
            temp_agencies = self._get_state_agencies_for_state(state_lower, context.country)
            
            if "environment" in temp_agencies or "environmental_management" in temp_agencies or "environmental_protection" in temp_agencies:
                # Simulate API call to state environmental agency
                data = {
                    "state": context.state_province or state,
                    "country": context.country,
                    "environmental_regulations": "current_regulations",
                    "water_quality_data": "monitoring_data",
                    "air_quality_data": "monitoring_data",
                    "extreme_weather_risk_assessments": "risk_data",
                    "agency_url": temp_agencies.get("environment") or temp_agencies.get("environmental_management") or temp_agencies.get("environmental_protection")
                }
                return {
                    "status": "success",
                    "data": data,
                    "disclaimer": "Decision support tool - results are for user review only"
                }
            else:
                return {"status": "error", "error": f"No environmental agency data for {state}"}

        except Exception as e:
            logger.error(f"Error fetching state environmental data: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_state_commerce_data(self, state: str) -> dict[str, Any]:
        """
        Get state commerce/economic development data.
        
        NOTE: This is a decision support tool. Results are reference examples for user review only.
        
        Args:
            state: State name
        
        Returns:
            Dict containing commerce data for the state
        """
        try:
            location_str = f"{state}, {self.country.upper()}" if self.country else state
            context = self.geography_parser.parse_location(location_str)
            state_lower = context.state_province.lower() if context.state_province else state.lower()
            temp_agencies = self._get_state_agencies_for_state(state_lower, context.country)
            
            if "commerce" in temp_agencies or "economic_opportunity" in temp_agencies:
                data = {
                    "state": context.state_province or state,
                    "country": context.country,
                    "economic_development_programs": "program_data",
                    "business_incentives": "incentive_data",
                    "infrastructure_investments": "investment_data",
                    "agency_url": temp_agencies.get("commerce") or temp_agencies.get("economic_opportunity")
                }
                return {
                    "status": "success",
                    "data": data,
                    "disclaimer": "Decision support tool - results are for user review only"
                }
            else:
                return {"status": "error", "error": f"No commerce agency data for {state}"}

        except Exception as e:
            logger.error(f"Error fetching state commerce data: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_state_transportation_data(self, state: str) -> dict[str, Any]:
        """
        Get state transportation data.
        
        NOTE: This is a decision support tool. Results are reference examples for user review only.
        
        Args:
            state: State name
        
        Returns:
            Dict containing transportation data for the state
        """
        try:
            location_str = f"{state}, {self.country.upper()}" if self.country else state
            context = self.geography_parser.parse_location(location_str)
            state_lower = context.state_province.lower() if context.state_province else state.lower()
            
            # Note: Transportation agencies not yet in agency mapping - placeholder
            data = {
                "state": context.state_province or state,
                "country": context.country,
                "transportation_infrastructure": "infrastructure_data",
                "extreme_weather_resilience": "resilience_data",
                "note": "Transportation agency data source needs to be added to agency mapping"
            }
            return {
                "status": "success",
                "data": data,
                "disclaimer": "Decision support tool - results are for user review only"
            }

        except Exception as e:
            logger.error(f"Error fetching state transportation data: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_state_emergency_mgmt_data(self, state: str) -> dict[str, Any]:
        """
        Get state emergency management data.
        
        NOTE: This is a decision support tool. Results are reference examples for user review only.
        
        Args:
            state: State name
        
        Returns:
            Dict containing emergency management data for the state
        """
        try:
            location_str = f"{state}, {self.country.upper()}" if self.country else state
            context = self.geography_parser.parse_location(location_str)
            state_lower = context.state_province.lower() if context.state_province else state.lower()
            temp_agencies = self._get_state_agencies_for_state(state_lower, context.country)
            
            if "emergency_management" in temp_agencies or "disaster_management" in temp_agencies:
                data = {
                    "state": context.state_province or state,
                    "country": context.country,
                    "extreme_weather_preparedness": "preparedness_data",
                    "emergency_response_plans": "response_plans",
                    "disaster_recovery_programs": "recovery_programs",
                    "agency_url": temp_agencies.get("emergency_management") or temp_agencies.get("disaster_management")
                }
                return {
                    "status": "success",
                    "data": data,
                    "disclaimer": "Decision support tool - results are for user review only"
                }
            else:
                return {"status": "error", "error": f"No emergency management agency data for {state}"}

        except Exception as e:
            logger.error(f"Error fetching state emergency management data: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_local_government_data(
        self,
        location: str,
        agency_type: str,
        administrative_level: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get local government data at any administrative level.
        
        NOTE: This is a decision support tool. Results are reference examples for user review only.
        Supports US (State → County → City) and India (State → District → Block → Village) hierarchies.
        
        Args:
            location: Location string (e.g., "Mobile Bay, Alabama", "Chennai, Tamil Nadu, India")
            agency_type: Type of agency (environmental, commerce, transportation, emergency_mgmt)
            administrative_level: Optional explicit level (auto-detected if not provided)
        
        Returns:
            Dict containing local government data
        """
        try:
            # Parse location to identify administrative hierarchy
            context = self.geography_parser.parse_location(location)
            
            if not context.country:
                return {
                    "status": "error",
                    "error": f"Could not identify country for location: {location}. Supported countries: US, India"
                }
            
            # Auto-detect administrative level if not provided
            if not administrative_level:
                administrative_level = context.administrative_level
            
            # Route to appropriate data source based on level
            if administrative_level == "state":
                if agency_type == "environmental":
                    return await self.get_state_environmental_data(context.state_province or location)
                elif agency_type == "commerce":
                    return await self.get_state_commerce_data(context.state_province or location)
                elif agency_type == "transportation":
                    return await self.get_state_transportation_data(context.state_province or location)
                elif agency_type == "emergency_mgmt":
                    return await self.get_state_emergency_mgmt_data(context.state_province or location)
                else:
                    return {"status": "error", "error": f"Unknown agency type: {agency_type}"}
            
            elif administrative_level in ["county", "district"]:
                # County (US) or District (India) level data
                data = {
                    "location": location,
                    "administrative_level": administrative_level,
                    "country": context.country,
                    "county_district": context.district_county,
                    "state": context.state_province,
                    "agency_type": agency_type,
                    "note": f"{administrative_level.title()}-level data access - implementation depends on available data sources",
                    "disclaimer": "Decision support tool - results are for user review only"
                }
                return {"status": "success", "data": data}
            
            elif administrative_level in ["city", "block"]:
                # City (US) or Block (India) level data
                data = {
                    "location": location,
                    "administrative_level": administrative_level,
                    "country": context.country,
                    "city_block": context.block_city,
                    "county_district": context.district_county,
                    "state": context.state_province,
                    "agency_type": agency_type,
                    "note": f"{administrative_level.title()}-level data access - implementation depends on available data sources",
                    "disclaimer": "Decision support tool - results are for user review only"
                }
                return {"status": "success", "data": data}
            
            elif administrative_level in ["neighborhood", "village"]:
                # Neighborhood (US) or Village (India) level data
                data = {
                    "location": location,
                    "administrative_level": administrative_level,
                    "country": context.country,
                    "village_neighborhood": context.village_neighborhood,
                    "city_block": context.block_city,
                    "county_district": context.district_county,
                    "state": context.state_province,
                    "agency_type": agency_type,
                    "note": f"{administrative_level.title()}-level data access - implementation depends on available data sources",
                    "disclaimer": "Decision support tool - results are for user review only"
                }
                return {"status": "success", "data": data}
            
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported administrative level: {administrative_level}. Supported levels: state, county/district, city/block, neighborhood/village"
                }

        except Exception as e:
            logger.error(f"Error fetching local government data: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_manufacturing_facility_risk_data(
        self,
        location: str,
        facility_type: str
    ) -> dict[str, Any]:
        """
        Get manufacturing facility risk data for extreme weather events.
        
        NOTE: This is a decision support tool. Results are reference examples for user review only.
        
        Args:
            location: Location of the facility
            facility_type: Type of manufacturing facility
        
        Returns:
            Dict containing risk data for the facility
        """
        try:
            context = self.geography_parser.parse_location(location)
            
            data = {
                "location": location,
                "facility_type": facility_type,
                "country": context.country,
                "state": context.state_province,
                "extreme_weather_risks": "risk_assessment_data",
                "infrastructure_resilience": "resilience_metrics",
                "mitigation_recommendations": "recommendation_data",
                "disclaimer": "Decision support tool - results are for user review only. Not automated decision-making."
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching manufacturing facility risk data: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_shipbuilding_industry_data(self) -> dict[str, Any]:
        """
        Get shipbuilding industry data.
        
        NOTE: This is a decision support tool. Results are reference examples for user review only.
        
        Returns:
            Dict containing shipbuilding industry data
        """
        try:
            data = {
                "industry": "shipbuilding",
                "extreme_weather_impacts": "impact_data",
                "coastal_facility_risks": "risk_data",
                "resilience_considerations": "consideration_data",
                "disclaimer": "Decision support tool - results are for user review only"
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching shipbuilding industry data: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_construction_cost_data(
        self,
        location: str,
        facility_type: str
    ) -> dict[str, Any]:
        """
        Get construction cost data for a location and facility type.
        
        NOTE: This is a decision support tool. Results are reference examples for user review only.
        Cost estimates are ranges only, not guarantees.
        
        Args:
            location: Location for construction
            facility_type: Type of facility
        
        Returns:
            Dict containing construction cost data
        """
        try:
            context = self.geography_parser.parse_location(location)
            
            data = {
                "location": location,
                "facility_type": facility_type,
                "country": context.country,
                "state": context.state_province,
                "cost_estimates": "cost_range_data",
                "extreme_weather_resilience_costs": "resilience_cost_data",
                "note": "Cost estimates are ranges only, not guarantees",
                "disclaimer": "Decision support tool - results are for user review only. Not financial guarantees."
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching construction cost data: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_state_agencies_for_state(self, state: str, country: Optional[str] = None) -> dict[str, str]:
        """
        Helper method to get agencies for a specific state.
        
        Args:
            state: State name (lowercase)
            country: Country code (us or india)
        
        Returns:
            Dict of agency URLs
        """
        us_agencies = {
            "kansas": {
                "water_office": "https://www.kwo.ks.gov",
                "geological_survey": "https://www.kgs.ku.edu",
                "agriculture": "https://agriculture.ks.gov",
                "environment": "https://www.kdhe.ks.gov"
            },
            "florida": {
                "environmental_protection": "https://floridadep.gov",
                "agriculture": "https://www.fdacs.gov",
                "economic_opportunity": "https://floridajobs.org",
                "emergency_management": "https://www.floridadisaster.org"
            },
            "north_carolina": {
                "environmental_quality": "https://deq.nc.gov",
                "agriculture": "https://www.ncagr.gov",
                "commerce": "https://www.nccommerce.com",
                "emergency_management": "https://www.ncdps.gov"
            },
            "alabama": {
                "environmental_management": "https://adem.alabama.gov",
                "agriculture": "https://agi.alabama.gov",
                "commerce": "https://www.madeinalabama.com",
                "emergency_management": "https://ema.alabama.gov"
            }
        }
        
        india_agencies = {
            "tamil nadu": {
                "environment": "https://www.tnenvis.nic.in",
                "agriculture": "https://www.tnagri.gov.in",
                "commerce": "https://www.tn.gov.in",
                "disaster_management": "https://www.tn.gov.in"
            },
            "maharashtra": {
                "environment": "https://www.mpcb.gov.in",
                "agriculture": "https://www.mahaagri.gov.in",
                "commerce": "https://www.maharashtra.gov.in",
                "disaster_management": "https://www.maharashtra.gov.in"
            }
        }
        
        if country == "india":
            if "tamil" in state and "nadu" in state:
                return india_agencies.get("tamil nadu", {})
            return india_agencies.get(state, {})
        elif country == "us" or country is None:
            return us_agencies.get(state, {})
        else:
            return {}

class EconomicData(EnhancedDataSource):
    """Economic and financial data sources."""

    def __init__(self):
        super().__init__()
        self.sources = {
            "federal_reserve": "https://api.stlouisfed.org/fred",
            "bls": "https://api.bls.gov/publicAPI/v2",
            "census": "https://api.census.gov/data"
        }

    async def fetch_data(self, **kwargs) -> dict[str, Any]:
        """Fetch economic data."""
        try:
            location = kwargs.get("location", "")
            data_type = kwargs.get("data_type", "economic")
            
            if data_type == "economic":
                return await self.get_regional_economic_data(location)
            elif data_type == "agricultural_finance":
                return await self.get_agricultural_finance_data(location)
            else:
                return {"status": "error", "error": f"Unknown data type: {data_type}"}
                
        except Exception as e:
            return self.handle_error(e)

    async def get_regional_economic_data(self, region: str) -> dict[str, Any]:
        """Get regional economic indicators."""
        try:
            # Simulate Federal Reserve Economic Data (FRED) API call
            data = {
                "region": region,
                "employment_rate": "current_employment_data",
                "income_levels": "median_income_data",
                "economic_growth": "gdp_growth_data",
                "inflation_rate": "price_index_data"
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching economic data: {e}")
            return {"status": "error", "error": str(e)}

    async def get_agricultural_finance_data(self, state: str) -> dict[str, Any]:
        """Get agricultural finance and lending data."""
        try:
            # Simulate agricultural finance data
            data = {
                "state": state,
                "farm_income": "income_statistics",
                "land_values": "property_values",
                "lending_trends": "loan_data",
                "commodity_prices": "market_prices"
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching agricultural finance data: {e}")
            return {"status": "error", "error": str(e)}

class InfrastructureData(EnhancedDataSource):
    """Infrastructure and development data sources."""

    def __init__(self):
        super().__init__()
        self.sources = {
            "dot": "https://www.transportation.gov/data",
            "eia": "https://www.eia.gov/opendata",
            "fema": "https://www.fema.gov/openfema"
        }

    async def fetch_data(self, **kwargs) -> dict[str, Any]:
        """Fetch infrastructure data."""
        try:
            location = kwargs.get("location", "")
            data_type = kwargs.get("data_type", "infrastructure")
            
            if data_type == "infrastructure":
                return await self.get_infrastructure_resilience_data(location)
            elif data_type == "development":
                return await self.get_development_project_data(location)
            else:
                return {"status": "error", "error": f"Unknown data type: {data_type}"}
                
        except Exception as e:
            return self.handle_error(e)

    async def get_infrastructure_resilience_data(self, location: str) -> dict[str, Any]:
        """Get infrastructure resilience and vulnerability data."""
        try:
            # Simulate infrastructure data
            data = {
                "location": location,
                "transportation": "road_network_data",
                "energy": "power_grid_data",
                "water": "water_system_data",
                "communications": "telecom_data"
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching infrastructure data: {e}")
            return {"status": "error", "error": str(e)}

    async def get_development_project_data(self, region: str) -> dict[str, Any]:
        """Get development project and investment data."""
        try:
            # Simulate development data
            data = {
                "region": region,
                "projects": "development_projects",
                "investments": "investment_data",
                "permits": "construction_permits",
                "timelines": "project_schedules"
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching development data: {e}")
            return {"status": "error", "error": str(e)}

class RegulatoryData(EnhancedDataSource):
    """Regulatory and compliance data sources."""

    def __init__(self):
        super().__init__()
        self.sources = {
            "irs": "https://www.irs.gov",
            "epa": "https://www.epa.gov",
            "fema": "https://www.fema.gov"
        }

    async def fetch_data(self, **kwargs) -> dict[str, Any]:
        """Fetch regulatory data."""
        try:
            location = kwargs.get("location", "")
            data_type = kwargs.get("data_type", "regulatory")
            
            if data_type == "opportunity_zone":
                return await self.get_opportunity_zone_data(location)
            elif data_type == "environmental_compliance":
                return await self.get_environmental_compliance_data(location)
            else:
                return {"status": "error", "error": f"Unknown data type: {data_type}"}
                
        except Exception as e:
            return self.handle_error(e)

    async def get_opportunity_zone_data(self, state: str) -> dict[str, Any]:
        """Get Opportunity Zone compliance and investment data."""
        try:
            # Simulate QOZ data
            data = {
                "state": state,
                "designated_zones": "zone_boundaries",
                "investment_requirements": "compliance_rules",
                "tax_benefits": "benefit_calculations",
                "success_stories": "case_studies"
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching QOZ data: {e}")
            return {"status": "error", "error": str(e)}

    async def get_environmental_compliance_data(self, location: str) -> dict[str, Any]:
        """Get environmental compliance and permitting data."""
        try:
            # Simulate environmental compliance data
            data = {
                "location": location,
                "permits": "environmental_permits",
                "regulations": "compliance_requirements",
                "inspections": "inspection_data",
                "violations": "violation_history"
            }
            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Error fetching compliance data: {e}")
            return {"status": "error", "error": str(e)}

class EnhancedDataManager:
    """Manager for enhanced data sources."""

    def __init__(self):
        self.sources = {}
        self._initialize_sources()

    def _initialize_sources(self):
        """Initialize all enhanced data sources."""
        self.sources["usda_water"] = USDAWaterData()
        self.sources["economic"] = EconomicData()
        self.sources["infrastructure"] = InfrastructureData()
        self.sources["regulatory"] = RegulatoryData()

    def get_state_agency_data(self, state: str = None, location: str = None) -> StateAgencyData:
        """
        Get state-specific agency data source.
        
        Args:
            state: State name (for backward compatibility)
            location: Location string (e.g., "Mobile Bay, Alabama" or "Chennai, Tamil Nadu, India")
        
        Returns:
            StateAgencyData instance
        """
        if location:
            return StateAgencyData(location=location)
        elif state:
            return StateAgencyData(state=state)
        else:
            raise ValueError("Either 'state' or 'location' must be provided")

    async def get_comprehensive_data(self, location: str, data_types: list[str]) -> dict[str, Any]:
        """Get comprehensive data from multiple sources."""
        results = {}

        for data_type in data_types:
            if data_type == "water":
                results["water"] = await self.sources["usda_water"].get_drought_data(location)
            elif data_type == "economic":
                results["economic"] = await self.sources["economic"].get_regional_economic_data(location)
            elif data_type == "infrastructure":
                results["infrastructure"] = await self.sources["infrastructure"].get_infrastructure_resilience_data(location)
            elif data_type == "regulatory":
                results["regulatory"] = await self.sources["regulatory"].get_environmental_compliance_data(location)

        return results

    def get_available_sources(self) -> list[str]:
        """Get list of available data sources."""
        return list(self.sources.keys())

    def get_source_metadata(self, source_name: str) -> dict[str, Any]:
        """Get metadata for a specific data source."""
        if source_name in self.sources:
            return {
                "name": source_name,
                "class": self.sources[source_name].__class__.__name__,
                "cache_dir": str(self.sources[source_name].cache_dir),
                "cache_expiry": str(self.sources[source_name].cache_expiry)
            }
        else:
            return {"error": f"Source {source_name} not found"}

# Global instance for easy access
enhanced_data_manager = EnhancedDataManager()
