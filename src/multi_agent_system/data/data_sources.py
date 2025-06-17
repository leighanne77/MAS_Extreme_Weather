"""
Data Sources Integration Module

This module provides a unified interface for multiple weather data sources,
including NOAA SWDI, and allows for data aggregation and comparison.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import pandas as pd
import logging
from pathlib import Path
import json
import hashlib
from functools import lru_cache

from .data_source import DataSource
from .nature_based_solutions_source import NatureBasedSolutionsSource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherDataSource(ABC):
    """Abstract base class for weather data sources."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize the data source.
        
        Args:
            cache_dir (str): Directory for caching data
        """
        self.cache_dir = Path(cache_dir) / self.__class__.__name__.lower()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = timedelta(hours=1)
        
    @abstractmethod
    def get_data(
        self,
        location: str,
        start_date: str,
        end_date: str,
        data_type: str = "all",
        force_refresh: bool = False
    ) -> Dict:
        """Get data from the source."""
        pass
        
    @abstractmethod
    def get_metadata(self) -> Dict:
        """Get metadata about available data."""
        pass
        
    def _get_cache_key(self, params: Dict) -> str:
        """Generate a unique cache key."""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()
        
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{cache_key}.json"
        
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is valid."""
        if not cache_path.exists():
            return False
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age < self.cache_expiry
        
    def _save_to_cache(self, data: Dict, cache_path: Path):
        """Save data to cache."""
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to save to cache: {e}")
            
    def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load data from cache."""
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
            return None

class NOAASWDISource(WeatherDataSource):
    """NOAA Severe Weather Data Inventory source."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://www.ncei.noaa.gov/pub/data/swdi"
        self.api_key = api_key
        
    def get_data(
        self,
        location: str,
        start_date: str,
        end_date: str,
        data_type: str = "all",
        force_refresh: bool = False
    ) -> Dict:
        """Get data from NOAA SWDI."""
        params = {
            "location": location,
            "startDate": start_date,
            "endDate": end_date,
            "dataType": data_type
        }
        
        cache_key = self._get_cache_key(params)
        cache_path = self._get_cache_path(cache_key)
        
        if not force_refresh and self._is_cache_valid(cache_path):
            logger.info("Loading NOAA data from cache")
            cached_data = self._load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data
                
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/data",
                params=params,
                headers={"token": self.api_key} if self.api_key else {}
            )
            response.raise_for_status()
            data = response.json()
            
            self._save_to_cache(data, cache_path)
            return data
            
        except Exception as e:
            logger.error(f"NOAA API request failed: {e}")
            return {"status": "error", "error": str(e)}
            
    def get_metadata(self) -> Dict:
        """Get NOAA SWDI metadata."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/metadata")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch NOAA metadata: {e}")
            return {"status": "error", "error": str(e)}

class WeatherDataManager:
    """Manager for multiple weather data sources."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize the weather data manager.
        
        Args:
            cache_dir (str): Base directory for caching
        """
        self.sources: Dict[str, WeatherDataSource] = {}
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def add_source(self, name: str, source: WeatherDataSource):
        """Add a data source."""
        self.sources[name] = source
        
    def get_data(
        self,
        location: str,
        start_date: str,
        end_date: str,
        sources: Optional[List[str]] = None,
        data_type: str = "all",
        force_refresh: bool = False
    ) -> Dict:
        """
        Get data from multiple sources.
        
        Args:
            location (str): Location to get data for
            start_date (str): Start date
            end_date (str): End date
            sources (List[str], optional): List of sources to use
            data_type (str): Type of data to retrieve
            force_refresh (bool): Force refresh data
            
        Returns:
            Dict: Combined data from all sources
        """
        results = {}
        
        # Use all sources if none specified
        sources_to_use = sources or list(self.sources.keys())
        
        for source_name in sources_to_use:
            if source_name not in self.sources:
                logger.warning(f"Source {source_name} not found")
                continue
                
            try:
                source_data = self.sources[source_name].get_data(
                    location=location,
                    start_date=start_date,
                    end_date=end_date,
                    data_type=data_type,
                    force_refresh=force_refresh
                )
                results[source_name] = source_data
            except Exception as e:
                logger.error(f"Error getting data from {source_name}: {e}")
                results[source_name] = {"status": "error", "error": str(e)}
                
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "sources": results
        }
        
    def get_metadata(self, sources: Optional[List[str]] = None) -> Dict:
        """Get metadata from all sources."""
        results = {}
        sources_to_use = sources or list(self.sources.keys())
        
        for source_name in sources_to_use:
            if source_name not in self.sources:
                continue
            results[source_name] = self.sources[source_name].get_metadata()
            
        return results

def get_weather_data(
    location: str,
    time_period: str,
    sources: Optional[List[str]] = None,
    force_refresh: bool = False
) -> Dict:
    """
    Function-based tool for retrieving weather data from multiple sources.
    
    Args:
        location (str): Location to get data for
        time_period (str): Time period for data retrieval
        sources (List[str], optional): List of sources to use
        force_refresh (bool): Force refresh data
        
    Returns:
        Dict: Combined weather data from all sources
    """
    try:
        # Initialize data manager
        manager = WeatherDataManager()
        
        # Add NOAA source
        manager.add_source("noaa", NOAASWDISource())
        
        # Parse time period
        start_date, end_date = time_period.split(" to ")
        
        # Get data from all sources
        data = manager.get_data(
            location=location,
            start_date=start_date,
            end_date=end_date,
            sources=sources,
            force_refresh=force_refresh
        )
        
        return {
            "status": "success",
            "data": data,
            "cache_info": {
                "cached": not force_refresh,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

class DataSourceManager:
    """Manages data sources for the system.
    
    Attributes:
        sources (Dict[str, DataSource]): Registered data sources
    """
    
    def __init__(self):
        """Initialize the data source manager."""
        self.sources = {}
        self._register_default_sources()
        
    def _register_default_sources(self):
        """Register default data sources."""
        # Register nature-based solutions source
        self.register_source("nature_based_solutions", NatureBasedSolutionsSource())
        
    def register_source(self, name: str, source: DataSource):
        """Register a new data source.
        
        Args:
            name (str): Name of the data source
            source (DataSource): Data source instance
        """
        self.sources[name] = source
        logger.info(f"Registered data source: {name}")
        
    def get_source(self, name: str) -> Optional[DataSource]:
        """Get a registered data source.
        
        Args:
            name (str): Name of the data source
            
        Returns:
            Optional[DataSource]: Data source instance if found
        """
        return self.sources.get(name)
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for all data sources.
        
        Returns:
            Dict[str, Any]: Metrics for all data sources
        """
        return {
            name: source.get_metrics()
            for name, source in self.sources.items()
        } 