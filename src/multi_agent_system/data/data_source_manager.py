"""
DataSourceManager - Unified Data Source Registry

This module provides a single, consolidated interface for all data sources
in the MAS system. It replaces the fragmented approach of DataLoader,
DataManager, and EnhancedDataManager with a unified registry.

Usage:
    from multi_agent_system.data import get_data_source_manager
    
    dsm = get_data_source_manager()
    
    # Get JSON data
    solutions = dsm.get_json_data("nature_based_solutions")
    
    # List all sources
    for info in dsm.list_sources():
        print(f"{info.name}: {info.source_type.value}")
    
    # Health check
    health = dsm.health_check()

Date Created: January 14, 2026
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .data_enums import DataSourceType, DataLoadStatus

logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class DataSourceNotFoundError(Exception):
    """Raised when a required data source is not found in the registry."""
    
    def __init__(self, source_name: str, available_sources: List[str] = None):
        self.source_name = source_name
        self.available_sources = available_sources or []
        message = f"Data source '{source_name}' not found."
        if self.available_sources:
            message += f" Available sources: {', '.join(self.available_sources[:10])}"
        super().__init__(message)


class DataSourceUnavailableError(Exception):
    """Raised when a data source is registered but currently unavailable."""
    
    def __init__(self, source_name: str, reason: str = None):
        self.source_name = source_name
        self.reason = reason
        message = f"Data source '{source_name}' is unavailable."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DataSourceInfo:
    """Metadata about a registered data source."""
    
    name: str
    source_type: DataSourceType
    description: str = ""
    source: Any = None  # The actual source object/callable
    is_available: bool = True
    last_health_check: Optional[datetime] = None
    last_access: Optional[datetime] = None
    access_count: int = 0
    cache_ttl_seconds: int = 300  # 5 minutes default
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "source_type": self.source_type.value if self.source_type else None,
            "description": self.description,
            "is_available": self.is_available,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "last_access": self.last_access.isoformat() if self.last_access else None,
            "access_count": self.access_count,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "metadata": self.metadata
        }


# =============================================================================
# DATA SOURCE MANAGER
# =============================================================================

class DataSourceManager:
    """
    Unified manager for all data sources in the MAS system.
    
    This class provides:
    - Dynamic registration/unregistration of data sources
    - Lookup by name or type
    - Health monitoring
    - Metrics collection
    - Caching with TTL
    - Backward compatibility with DataLoader methods
    
    Singleton pattern ensures only one instance exists.
    """
    
    _instance: Optional["DataSourceManager"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "DataSourceManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the DataSourceManager (only runs once due to singleton)."""
        if DataSourceManager._initialized:
            return
        
        self._sources: Dict[str, DataSourceInfo] = {}
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._data_dir: Path = Path(__file__).parent
        
        # Auto-register JSON sources
        self._register_json_sources()
        
        # Auto-register API sources
        self._register_api_sources()
        
        DataSourceManager._initialized = True
        logger.info("DataSourceManager initialized with %d sources", len(self._sources))
    
    # =========================================================================
    # REGISTRATION METHODS
    # =========================================================================
    
    def register_source(
        self,
        name: str,
        source: Any,
        source_type: DataSourceType,
        description: str = "",
        cache_ttl_seconds: int = 300,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Register a data source with the manager.
        
        Args:
            name: Unique identifier for the source
            source: The source object (callable, class instance, or path)
            source_type: Type of data source (JSON, API, etc.)
            description: Human-readable description
            cache_ttl_seconds: Cache time-to-live in seconds
            metadata: Additional metadata about the source
        
        Raises:
            ValueError: If a source with this name already exists
        """
        if name in self._sources:
            logger.warning("Overwriting existing source: %s", name)
        
        info = DataSourceInfo(
            name=name,
            source_type=source_type,
            description=description,
            source=source,
            cache_ttl_seconds=cache_ttl_seconds,
            metadata=metadata or {}
        )
        
        self._sources[name] = info
        logger.debug("Registered source: %s (%s)", name, source_type.value)
    
    def unregister_source(self, name: str) -> bool:
        """
        Remove a data source from the registry.
        
        Args:
            name: Name of the source to remove
            
        Returns:
            True if source was removed, False if not found
        """
        if name in self._sources:
            del self._sources[name]
            # Clear cache for this source
            if name in self._cache:
                del self._cache[name]
            if name in self._cache_timestamps:
                del self._cache_timestamps[name]
            logger.debug("Unregistered source: %s", name)
            return True
        return False
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    def get_source(self, name: str, required: bool = False) -> Optional[DataSourceInfo]:
        """
        Get a data source by name.
        
        Args:
            name: Name of the source
            required: If True, raise exception when not found
            
        Returns:
            DataSourceInfo or None if not found (and not required)
            
        Raises:
            DataSourceNotFoundError: If required and source not found
        """
        info = self._sources.get(name)
        
        if info is None and required:
            raise DataSourceNotFoundError(name, list(self._sources.keys()))
        
        if info:
            info.last_access = datetime.now()
            info.access_count += 1
        
        return info
    
    def get_sources_by_type(self, source_type: DataSourceType) -> List[DataSourceInfo]:
        """
        Get all sources of a specific type.
        
        Args:
            source_type: The type to filter by
            
        Returns:
            List of matching DataSourceInfo objects
        """
        return [
            info for info in self._sources.values()
            if info.source_type == source_type
        ]
    
    def list_sources(self) -> List[DataSourceInfo]:
        """
        List all registered data sources.
        
        Returns:
            List of all DataSourceInfo objects
        """
        return list(self._sources.values())
    
    def get_source_names(self) -> List[str]:
        """Get list of all registered source names."""
        return list(self._sources.keys())
    
    # =========================================================================
    # DATA ACCESS METHODS
    # =========================================================================
    
    def get_json_data(self, source_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load data from a JSON source.
        
        Args:
            source_name: Name of the JSON source
            use_cache: Whether to use cached data if available
            
        Returns:
            Parsed JSON data as dictionary
            
        Raises:
            DataSourceNotFoundError: If source not found
            DataSourceUnavailableError: If file cannot be read
        """
        info = self.get_source(source_name, required=True)
        
        if info.source_type != DataSourceType.JSON:
            raise ValueError(f"Source '{source_name}' is not a JSON source")
        
        # Check cache
        if use_cache and self._is_cache_valid(source_name, info.cache_ttl_seconds):
            logger.debug("Cache hit for: %s", source_name)
            return self._cache[source_name]
        
        # Load from file
        try:
            file_path = info.source if isinstance(info.source, Path) else Path(info.source)
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Update cache
            self._cache[source_name] = data
            self._cache_timestamps[source_name] = datetime.now()
            info.is_available = True
            
            logger.debug("Loaded JSON data: %s (%d bytes)", source_name, len(str(data)))
            return data
            
        except FileNotFoundError as e:
            info.is_available = False
            raise DataSourceUnavailableError(source_name, f"File not found: {e}") from e
        except json.JSONDecodeError as e:
            info.is_available = False
            raise DataSourceUnavailableError(source_name, f"Invalid JSON: {e}") from e
    
    def _is_cache_valid(self, source_name: str, ttl_seconds: int) -> bool:
        """Check if cached data is still valid."""
        if source_name not in self._cache:
            return False
        if source_name not in self._cache_timestamps:
            return False
        
        age = datetime.now() - self._cache_timestamps[source_name]
        return age.total_seconds() < ttl_seconds
    
    def clear_cache(self, source_name: str = None) -> None:
        """
        Clear cached data.
        
        Args:
            source_name: Specific source to clear, or None for all
        """
        if source_name:
            self._cache.pop(source_name, None)
            self._cache_timestamps.pop(source_name, None)
            logger.debug("Cleared cache for: %s", source_name)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.debug("Cleared all cache")
    
    # =========================================================================
    # HEALTH & METRICS
    # =========================================================================
    
    def health_check(self, source_name: str = None) -> Dict[str, bool]:
        """
        Check health of data sources.
        
        Args:
            source_name: Specific source to check, or None for all
            
        Returns:
            Dictionary of source_name -> is_healthy
        """
        results = {}
        
        sources_to_check = (
            [self._sources[source_name]] if source_name and source_name in self._sources
            else self._sources.values()
        )
        
        for info in sources_to_check:
            try:
                if info.source_type == DataSourceType.JSON:
                    # Check if file exists
                    file_path = info.source if isinstance(info.source, Path) else Path(info.source)
                    is_healthy = file_path.exists()
                elif info.source_type == DataSourceType.API:
                    # For APIs, check if source object has a health method
                    if hasattr(info.source, 'health_check'):
                        is_healthy = info.source.health_check()
                    else:
                        is_healthy = info.is_available
                else:
                    is_healthy = info.is_available
                
                info.is_available = is_healthy
                info.last_health_check = datetime.now()
                results[info.name] = is_healthy
                
            except Exception as e:
                logger.warning("Health check failed for %s: %s", info.name, e)
                info.is_available = False
                info.last_health_check = datetime.now()
                results[info.name] = False
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for all data sources.
        
        Returns:
            Dictionary with metrics for each source and aggregate stats
        """
        source_metrics = {}
        total_access = 0
        available_count = 0
        
        for name, info in self._sources.items():
            source_metrics[name] = {
                "type": info.source_type.value,
                "is_available": info.is_available,
                "access_count": info.access_count,
                "last_access": info.last_access.isoformat() if info.last_access else None,
                "cached": name in self._cache
            }
            total_access += info.access_count
            if info.is_available:
                available_count += 1
        
        return {
            "total_sources": len(self._sources),
            "available_sources": available_count,
            "unavailable_sources": len(self._sources) - available_count,
            "total_access_count": total_access,
            "cache_size": len(self._cache),
            "sources": source_metrics
        }
    
    def get_source_status(self, name: str) -> Dict[str, Any]:
        """Get detailed status for a specific source."""
        info = self.get_source(name)
        if not info:
            return {"error": f"Source '{name}' not found"}
        return info.to_dict()
    
    # =========================================================================
    # BACKWARD COMPATIBILITY - DataLoader Methods
    # =========================================================================
    
    def load_nature_based_solutions(self) -> Dict[str, Any]:
        """Load nature-based solutions data. (DataLoader compat)"""
        return self.get_json_data("nature_based_solutions")
    
    def load_historical_weather_events(self) -> Dict[str, Any]:
        """Load historical weather events data. (DataLoader compat)"""
        return self.get_json_data("historical_weather_events")
    
    def load_economic_impact_data(self) -> Dict[str, Any]:
        """Load economic impact data. (DataLoader compat)"""
        return self.get_json_data("economic_impact_data")
    
    def load_regional_risk_profiles(self) -> Dict[str, Any]:
        """Load regional risk profiles data. (DataLoader compat)"""
        return self.get_json_data("regional_risk_profiles")
    
    def get_solution_by_id(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific nature-based solution by ID. (DataLoader compat)"""
        data = self.load_nature_based_solutions()
        for solution in data.get("solutions", []):
            if solution.get("id") == solution_id:
                return solution
        return None
    
    def get_solutions_by_risk_type(self, risk_type: str) -> List[Dict[str, Any]]:
        """Get solutions that address a specific risk type. (DataLoader compat)"""
        data = self.load_nature_based_solutions()
        return [
            s for s in data.get("solutions", [])
            if risk_type in s.get("risk_types", [])
        ]
    
    def get_solutions_by_location(self, location_type: str) -> List[Dict[str, Any]]:
        """Get solutions suitable for a location type. (DataLoader compat)"""
        data = self.load_nature_based_solutions()
        return [
            s for s in data.get("solutions", [])
            if location_type in s.get("suitable_locations", [])
        ]
    
    def get_solution_biodiversity_impact(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """Get biodiversity impact for a solution. (DataLoader compat)"""
        solution = self.get_solution_by_id(solution_id)
        if solution:
            return solution.get("biodiversity_impact")
        return None
    
    def get_regional_profile(self, region_name: str) -> Optional[Dict[str, Any]]:
        """Get risk profile for a specific region. (DataLoader compat)"""
        data = self.load_regional_risk_profiles()
        return data.get("regions", {}).get(region_name)
    
    def get_all_data_summary(self) -> Dict[str, Any]:
        """Get summary of all available data. (DataLoader compat)"""
        summary = {
            "nature_based_solutions": {"count": 0, "risk_types": set(), "location_types": set()},
            "historical_events": {"count": 0, "event_types": set(), "regions": set()},
            "regions": {"count": 0, "region_names": []}
        }
        
        try:
            nbs = self.load_nature_based_solutions()
            solutions = nbs.get("solutions", [])
            summary["nature_based_solutions"]["count"] = len(solutions)
            for s in solutions:
                summary["nature_based_solutions"]["risk_types"].update(s.get("risk_types", []))
                summary["nature_based_solutions"]["location_types"].update(s.get("suitable_locations", []))
        except Exception:
            pass
        
        try:
            events = self.load_historical_weather_events()
            event_list = events.get("events", [])
            summary["historical_events"]["count"] = len(event_list)
            for e in event_list:
                summary["historical_events"]["event_types"].add(e.get("type"))
                summary["historical_events"]["regions"].add(e.get("location", {}).get("region"))
        except Exception:
            pass
        
        try:
            profiles = self.load_regional_risk_profiles()
            regions = profiles.get("regions", {})
            summary["regions"]["count"] = len(regions)
            summary["regions"]["region_names"] = list(regions.keys())
        except Exception:
            pass
        
        # Convert sets to lists for JSON serialization
        summary["nature_based_solutions"]["risk_types"] = list(summary["nature_based_solutions"]["risk_types"])
        summary["nature_based_solutions"]["location_types"] = list(summary["nature_based_solutions"]["location_types"])
        summary["historical_events"]["event_types"] = list(summary["historical_events"]["event_types"])
        summary["historical_events"]["regions"] = list(summary["historical_events"]["regions"])
        
        return summary
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _register_json_sources(self) -> None:
        """Auto-register all JSON data sources."""
        json_sources = [
            # Core data files
            ("nature_based_solutions", "nature_based_solutions.json", 
             "Nature-based solutions database (45+ solutions with case studies)"),
            ("historical_weather_events", "historical_weather_events.json",
             "Historical extreme weather events"),
            ("weather_events", "historical_weather_events.json",
             "Historical weather events (alias)"),
            ("economic_impact_data", "economic_impact_data.json",
             "Economic impact data for weather events"),
            ("economic_impacts", "economic_impact_data.json",
             "Economic impacts (alias)"),
            ("regional_risk_profiles", "regional_risk_profiles.json",
             "Regional risk profiles for Gulf Coast and other regions"),
            
            # Funding and infrastructure
            ("funding_sources", "funding_sources_NSB.json",
             "Funding sources for nature-based solutions"),
            ("funding_sources_NSB", "funding_sources_NSB.json",
             "Funding sources for NSB (alias for demo compatibility)"),
            ("coastal_infrastructure", "coastal_areas_infrastructure_needs.json",
             "Coastal infrastructure needs assessment"),
            ("opportunity_zones", "opportunity_zones.json",
             "HUD Opportunity Zone data"),
            
            # Additional data files
            ("biodiversity_credits", "Biodiversity_Credit_Revenue_Streams.json",
             "Biodiversity credit revenue streams data"),
            ("regional_opportunities", "regional_opportunities.json",
             "Regional investment opportunities"),
            ("erddap_servers", "erddap_servers.json",
             "ERDDAP server registry"),
            ("government_data_sources", "government_data_sources_examples.json",
             "Government data source examples"),
            ("local_expert_knowledge", "local_expert_knowledge_data_sources_examples.json",
             "Local expert knowledge data sources"),
        ]
        
        for name, filename, description in json_sources:
            file_path = self._data_dir / filename
            if file_path.exists():
                self.register_source(
                    name=name,
                    source=file_path,
                    source_type=DataSourceType.JSON,
                    description=description,
                    cache_ttl_seconds=300  # 5 minute cache
                )
            else:
                logger.debug("JSON file not found, skipping: %s", filename)
    
    def _register_api_sources(self) -> None:
        """Register external API data sources."""
        # Import API modules lazily to avoid circular imports
        # Format: (name, module_name, func_name, metadata_name, description)
        api_sources = [
            # === Original 5 API sources ===
            ("bls_api", "bls_api", "get_bls_data", "BLS_TOOL_METADATA",
             "Bureau of Labor Statistics employment and wage data"),
            ("census_api", "census_api", "get_census_data", "CENSUS_TOOL_METADATA",
             "US Census Bureau demographic and economic data"),
            ("openfema_api", "openfema_api", "get_openfema_data", "OPENFEMA_TOOL_METADATA",
             "FEMA disaster declarations and hazard data"),
            ("eia_api", "eia_api", "get_eia_data", "EIA_TOOL_METADATA",
             "EIA energy production and consumption data"),
            ("usgs_water_api", "usgs_water", "usgs_water_query", None,
             "USGS Water Services hydrological data"),
            
            # === Additional API sources (no API key required) ===
            ("fhfa_api", "fhfa_api", "get_fhfa_data", "FHFA_TOOL_METADATA",
             "FHFA House Price Index and housing market data"),
            ("epa_storet_api", "epa_storet_api", "get_storet_data", None,
             "EPA STORET water quality monitoring data"),
            ("epa_wqx_api", "epa_wqx_api", "get_wqx_data", None,
             "EPA Water Quality Exchange (WQX) data"),
            ("osm_api", "osm_api", "get_osm_data", None,
             "OpenStreetMap Overpass API for geographic data"),
            
            # === API sources requiring API keys (function-based) ===
            ("usda_nass_api", "usda_nass_api", "get_nass_data", "USDA_NASS_TOOL_METADATA",
             "USDA NASS Quick Stats agricultural data (requires QUICKSTATS_API_KEY)"),
        ]
        
        for name, module_name, func_name, metadata_name, description in api_sources:
            try:
                # Lazy import of API module
                module = __import__(f"multi_agent_system.data.{module_name}", fromlist=[func_name])
                api_func = getattr(module, func_name)
                metadata = getattr(module, metadata_name, {}) if metadata_name else {}
                
                self.register_source(
                    name=name,
                    source=api_func,
                    source_type=DataSourceType.API,
                    description=description,
                    cache_ttl_seconds=metadata.get("cache_ttl", 3600),  # 1 hour default for APIs
                    metadata={
                        "module": module_name,
                        "function": func_name,
                        "domain": str(metadata.get("domain", "unknown")),
                        "update_frequency": str(metadata.get("update_frequency", "unknown")),
                        "access_level": str(metadata.get("access_level", "public")),
                    }
                )
                logger.debug("Registered API source: %s", name)
            except ImportError as e:
                logger.debug("API module not available, skipping %s: %s", name, e)
            except AttributeError as e:
                logger.debug("API function not found, skipping %s: %s", name, e)
        
        # === Class-based data providers ===
        # These require instantiation rather than simple function import
        self._register_class_based_providers()
    
    def _register_class_based_providers(self) -> None:
        """Register class-based data providers that need instantiation."""
        # FRED Data Source (requires FRED_API_KEY)
        try:
            from .fred_api import FREDDataSource
            fred_source = FREDDataSource()
            self.register_source(
                name="fred_api",
                source=fred_source,
                source_type=DataSourceType.API,
                description="Federal Reserve Economic Data (FRED) for economic indicators (requires FRED_API_KEY)",
                cache_ttl_seconds=21600,  # 6 hours
                metadata={
                    "module": "fred_api",
                    "class": "FREDDataSource",
                    "domain": "economic",
                    "update_frequency": "daily",
                    "access_level": "restricted",
                    "requires_api_key": True,
                }
            )
            logger.debug("Registered class-based API source: fred_api")
        except ImportError as e:
            logger.debug("FRED module not available: %s", e)
        except Exception as e:
            logger.debug("Failed to register FRED source: %s", e)
        
        # Data.gov Data Provider (no API key required)
        try:
            from .datagov_mcp import DataGovDataProvider
            datagov_source = DataGovDataProvider()
            self.register_source(
                name="datagov_api",
                source=datagov_source,
                source_type=DataSourceType.API,
                description="Data.gov catalog API for federal government datasets",
                cache_ttl_seconds=21600,  # 6 hours
                metadata={
                    "module": "datagov_mcp",
                    "class": "DataGovDataProvider",
                    "domain": "government",
                    "update_frequency": "daily",
                    "access_level": "public",
                    "requires_api_key": False,
                }
            )
            logger.debug("Registered class-based API source: datagov_api")
        except ImportError as e:
            logger.debug("DataGov module not available: %s", e)
        except Exception as e:
            logger.debug("Failed to register DataGov source: %s", e)
        
        # NASA CMR Data Provider (requires NASA_EARTHDATA_TOKEN)
        try:
            from .cmr_mcp import CMRDataProvider
            cmr_source = CMRDataProvider()
            self.register_source(
                name="cmr_api",
                source=cmr_source,
                source_type=DataSourceType.API,
                description="NASA Common Metadata Repository for Earth science data (requires NASA_EARTHDATA_TOKEN)",
                cache_ttl_seconds=21600,  # 6 hours
                metadata={
                    "module": "cmr_mcp",
                    "class": "CMRDataProvider",
                    "domain": "climate",
                    "update_frequency": "daily",
                    "access_level": "restricted",
                    "requires_api_key": True,
                }
            )
            logger.debug("Registered class-based API source: cmr_api")
        except ImportError as e:
            logger.debug("CMR module not available: %s", e)
        except Exception as e:
            logger.debug("Failed to register CMR source: %s", e)
        
        # ERDDAP Data Provider (no API key required)
        try:
            from .erddap_mcp import ERDDAPDataProvider
            erddap_source = ERDDAPDataProvider()
            self.register_source(
                name="erddap_api",
                source=erddap_source,
                source_type=DataSourceType.API,
                description="ERDDAP scientific data server access for ocean and climate data",
                cache_ttl_seconds=21600,  # 6 hours
                metadata={
                    "module": "erddap_mcp",
                    "class": "ERDDAPDataProvider",
                    "domain": "climate",
                    "update_frequency": "varies",
                    "access_level": "public",
                    "requires_api_key": False,
                }
            )
            logger.debug("Registered class-based API source: erddap_api")
        except ImportError as e:
            logger.debug("ERDDAP module not available: %s", e)
        except Exception as e:
            logger.debug("Failed to register ERDDAP source: %s", e)
        
        # NBI Loader (file-based, no API key required)
        try:
            from .nbi_loader import load_nbi_data
            self.register_source(
                name="nbi_loader",
                source=load_nbi_data,
                source_type=DataSourceType.API,  # Treated as API since it's a function
                description="National Bridge Inventory data loader",
                cache_ttl_seconds=86400,  # 24 hours (data doesn't change often)
                metadata={
                    "module": "nbi_loader",
                    "function": "load_nbi_data",
                    "domain": "infrastructure",
                    "update_frequency": "yearly",
                    "access_level": "public",
                    "requires_api_key": False,
                }
            )
            logger.debug("Registered loader source: nbi_loader")
        except ImportError as e:
            logger.debug("NBI loader not available: %s", e)
        except Exception as e:
            logger.debug("Failed to register NBI loader: %s", e)
        
        # OpenET Data Source (requires OPENET_API_KEY)
        try:
            from .openet_api import OpenETDataSource
            openet_source = OpenETDataSource()
            self.register_source(
                name="openet_api",
                source=openet_source,
                source_type=DataSourceType.API,
                description="OpenET evapotranspiration and water use data (requires OPENET_API_KEY)",
                cache_ttl_seconds=3600,  # 1 hour
                metadata={
                    "module": "openet_api",
                    "class": "OpenETDataSource",
                    "domain": "water",
                    "update_frequency": "daily",
                    "access_level": "restricted",
                    "requires_api_key": True,
                }
            )
            logger.debug("Registered class-based API source: openet_api")
        except ImportError as e:
            logger.debug("OpenET module not available: %s", e)
        except Exception as e:
            logger.debug("Failed to register OpenET source: %s", e)
    
    def call_api_source(
        self, 
        source_name: str, 
        *args, 
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call an API data source.
        
        Args:
            source_name: Name of the registered API source
            *args: Positional arguments to pass to the API function
            use_cache: Whether to use cached results
            **kwargs: Keyword arguments to pass to the API function
            
        Returns:
            API response data
            
        Raises:
            DataSourceNotFoundError: If source not found
            DataSourceUnavailableError: If API call fails
        """
        info = self.get_source(source_name, required=True)
        
        if info.source_type != DataSourceType.API:
            raise ValueError(f"Source '{source_name}' is not an API source")
        
        # Build cache key from args and kwargs
        cache_key = f"{source_name}:{args}:{sorted(kwargs.items())}"
        
        # Check cache
        if use_cache and self._is_cache_valid(cache_key, info.cache_ttl_seconds):
            logger.debug("Cache hit for API call: %s", source_name)
            return self._cache[cache_key]
        
        # Call the API
        try:
            api_func = info.source
            result = api_func(*args, **kwargs)
            
            # Update cache
            self._cache[cache_key] = result
            self._cache_timestamps[cache_key] = datetime.now()
            info.is_available = True
            
            logger.debug("API call successful: %s", source_name)
            return result
            
        except Exception as e:
            info.is_available = False
            logger.warning("API call failed for %s: %s", source_name, e)
            raise DataSourceUnavailableError(source_name, str(e)) from e
    
    def get_api_sources(self) -> List[DataSourceInfo]:
        """Get all registered API sources."""
        return self.get_sources_by_type(DataSourceType.API)
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None
        cls._initialized = False


# =============================================================================
# MODULE-LEVEL FUNCTIONS
# =============================================================================

def get_data_source_manager() -> DataSourceManager:
    """
    Get the global DataSourceManager instance.
    
    This is the primary entry point for accessing data sources.
    
    Returns:
        The singleton DataSourceManager instance
    """
    return DataSourceManager()
