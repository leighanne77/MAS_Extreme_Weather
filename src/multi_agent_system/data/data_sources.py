"""
Data Sources Integration Module

This module provides a unified interface for multiple weather data sources,
including NOAA SWDI, and allows for data aggregation and comparison.
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .data_source import DataSource
from .enhanced_data_sources import enhanced_data_manager
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
    ) -> dict:
        """Get data from the source."""
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        """Get metadata about available data."""
        pass

    def _get_cache_key(self, params: dict) -> str:
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

    def _save_to_cache(self, data: dict, cache_path: Path):
        """Save data to cache."""
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
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

class NOAASWDISource(WeatherDataSource):
    """NOAA Severe Weather Data Inventory source."""

    def __init__(self, api_key: str | None = None, **kwargs):
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
    ) -> dict:
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

    def get_metadata(self) -> dict:
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
        self.sources: dict[str, WeatherDataSource] = {}
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
        sources: list[str] | None = None,
        data_type: str = "all",
        force_refresh: bool = False
    ) -> dict:
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
            "data": results,
            "metadata": {
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "data_type": data_type,
                "sources": sources_to_use,
                "timestamp": datetime.now().isoformat()
            }
        }

    def get_metadata(self, sources: list[str] | None = None) -> dict:
        """Get metadata from all sources."""
        results = {}
        sources_to_use = sources or list(self.sources.keys())

        for source_name in sources_to_use:
            if source_name in self.sources:
                try:
                    results[source_name] = self.sources[source_name].get_metadata()
                except Exception as e:
                    logger.error(f"Error getting metadata from {source_name}: {e}")
                    results[source_name] = {"status": "error", "error": str(e)}

        return results

def get_weather_data(
    location: str,
    time_period: str,
    sources: list[str] | None = None,
    force_refresh: bool = False
) -> dict:
    """
    Get weather data for a location and time period.

    Args:
        location (str): Location to get weather data for
        time_period (str): Time period (e.g., "2024-01-01:2024-01-31")
        sources (List[str], optional): Data sources to use
        force_refresh (bool): Force refresh data

    Returns:
        Dict: Weather data from specified sources
    """
    try:
        # Parse time period
        if ":" in time_period:
            start_date, end_date = time_period.split(":")
        else:
            start_date = time_period
            end_date = time_period

        # Create weather data manager
        manager = WeatherDataManager()

        # Add NOAA source
        noaa_source = NOAASWDISource()
        manager.add_source("noaa", noaa_source)

        # Get data
        return manager.get_data(
            location=location,
            start_date=start_date,
            end_date=end_date,
            sources=sources,
            force_refresh=force_refresh
        )

    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        return {
            "status": "error",
            "error": str(e),
            "metadata": {
                "location": location,
                "time_period": time_period,
                "timestamp": datetime.now().isoformat()
            }
        }

class DataSourceManager:
    """Manager for all data sources including enhanced sources."""

    def __init__(self):
        """Initialize the data source manager."""
        self.sources = {}
        self.enhanced_sources = enhanced_data_manager
        self._register_default_sources()

    def _register_default_sources(self):
        """Register default data sources."""
        self.register_source("nature_based_solutions", NatureBasedSolutionsSource())

    def register_source(self, name: str, source: DataSource):
        """Register a new data source.

        Args:
            name (str): Name of the data source
            source (DataSource): Data source instance
        """
        self.sources[name] = source
        logger.info(f"Registered data source: {name}")

    def get_source(self, name: str) -> DataSource | None:
        """Get a data source by name.

        Args:
            name (str): Name of the data source

        Returns:
            Optional[DataSource]: Data source if found, None otherwise
        """
        return self.sources.get(name)

    def get_enhanced_source(self, name: str):
        """Get an enhanced data source by name.

        Args:
            name (str): Name of the enhanced data source

        Returns:
            Enhanced data source if found, None otherwise
        """
        return self.enhanced_sources.sources.get(name)

    def get_metrics(self) -> dict[str, Any]:
        """Get metrics from all data sources.

        Returns:
            Dict[str, Any]: Metrics from all sources
        """
        metrics = {
            "standard_sources": {},
            "enhanced_sources": self.enhanced_sources.get_metrics()
        }

        for name, source in self.sources.items():
            try:
                metrics["standard_sources"][name] = source.get_metrics()
            except Exception as e:
                logger.error(f"Error getting metrics from {name}: {e}")
                metrics["standard_sources"][name] = {"status": "error", "error": str(e)}

        return metrics

# Global instance for easy access
data_source_manager = DataSourceManager()
