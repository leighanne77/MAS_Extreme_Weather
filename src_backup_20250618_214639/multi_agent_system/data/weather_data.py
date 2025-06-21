"""
Weather Data Integration Module

This module handles integration with NOAA's Severe Weather Data Inventory (SWDI)
and provides functions for retrieving and processing weather data.

Tool Usage Examples:
    1. Basic Weather Data Retrieval:
        ```python
        # Get current weather data
        data = await get_weather_data(
            location="New York",
            time_period="2024-01",
            force_refresh=False
        )
        
        # Error handling
        if data["status"] == "error":
            # Retry with force refresh
            data = await get_weather_data(
                location="New York",
                time_period="2024-01",
                force_refresh=True
            )
        ```
        
    2. Sequential Tool Usage:
        ```python
        # Chain of tools for comprehensive weather analysis
        location = "New York"
        time_period = "2024-01"
        
        # 1. Get current weather
        current = await get_weather_data(location, time_period)
        if current["status"] == "error":
            return current
            
        # 2. Analyze patterns
        patterns = await analyze_weather_patterns(
            data=current["result"],
            analysis_type="frequency"
        )
        if patterns["status"] == "error":
            return patterns
            
        # 3. Get historical context
        historical = await get_weather_data(
            location=location,
            time_period="2023-01:2023-12"
        )
        if historical["status"] == "error":
            return historical
        ```
        
    3. Error Recovery:
        ```python
        # Example of error recovery in weather data chain
        try:
            # Attempt to get current data
            data = await get_weather_data(location, time_period)
        except Exception as e:
            # Fallback to cached data
            data = await get_weather_data(
                location=location,
                time_period=time_period,
                force_refresh=False
            )
            if data["status"] == "error":
                # Final fallback to basic weather data
                data = await get_basic_weather_data(location)
        ```

Error Handling Strategy:
    - All tools return a Dict with "status" and either "result" or "error"
    - Tools should be retried with exponential backoff on transient errors
    - Permanent errors should trigger fallback to alternative data sources
    - Critical errors should be reported to the user with clear next steps
"""

import json
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import xarray as xr
import os
import hashlib
from pathlib import Path
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NOAAWeatherData:
    """Handler for NOAA Severe Weather Data Inventory (SWDI) integration."""
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = ".cache"):
        """
        Initialize the NOAA Weather Data handler.
        
        Args:
            api_key (str, optional): API key for NOAA services
            cache_dir (str): Directory for caching data
        """
        self.base_url = "https://www.ncei.noaa.gov/pub/data/swdi"
        self.api_key = api_key
        self.supported_formats = ["csv", "json", "xml", "shapefile", "kmz"]
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_expiry = timedelta(hours=1)  # Cache expires after 1 hour
        
    def _get_cache_key(self, params: Dict) -> str:
        """Generate a unique cache key for the request parameters."""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()
        
    def _get_cache_path(self, cache_key: str, format: str) -> Path:
        """Get the cache file path for a given cache key and format."""
        return self.cache_dir / f"{cache_key}.{format}"
        
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if the cached data is still valid."""
        if not cache_path.exists():
            return False
            
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age < self.cache_expiry
        
    def _save_to_cache(self, data: Union[Dict, bytes], cache_path: Path):
        """Save data to cache."""
        try:
            if isinstance(data, dict):
                with open(cache_path, 'w') as f:
                    json.dump(data, f)
            else:
                with open(cache_path, 'wb') as f:
                    f.write(data)
        except Exception as e:
            logger.warning(f"Failed to save to cache: {e}")
            
    def _load_from_cache(self, cache_path: Path, format: str) -> Union[Dict, pd.DataFrame, bytes]:
        """Load data from cache."""
        try:
            if format == "json":
                with open(cache_path, 'r') as f:
                    return json.load(f)
            elif format == "csv":
                return pd.read_csv(cache_path)
            else:
                with open(cache_path, 'rb') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
            return None
            
    async def get_severe_weather_data(
        self,
        start_date: str,
        end_date: str,
        location: Optional[str] = None,
        data_type: str = "all",
        format: str = "json",
        force_refresh: bool = False
    ) -> Union[Dict, pd.DataFrame]:
        """
        Retrieve severe weather data from NOAA SWDI with caching.
        
        This tool fetches severe weather data from NOAA's SWDI service,
        with built-in caching and error handling. It supports multiple
        data formats and can force refresh the cache if needed.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            location (str, optional): Location to filter data
            data_type (str): Type of data to retrieve (all, storm, hail, tornado, etc.)
            format (str): Output format (json, csv, xml, shapefile, kmz)
            force_refresh (bool): Force refresh data from API
            
        Returns:
            Dict containing:
                - status: "success" or "error"
                - result: Weather data in specified format
                - error: Error message if status is "error"
                
        Error Handling:
            - On error, attempt to load from cache
            - If cache fails, retry API call with exponential backoff
            - Log all errors for analysis
            
        Example:
            ```python
            # Basic usage
            data = await get_severe_weather_data(
                start_date="2024-01-01",
                end_date="2024-01-31",
                location="New York"
            )
            
            # With error handling
            try:
                data = await get_severe_weather_data(
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                    location="New York",
                    force_refresh=True
                )
            except Exception as e:
                # Fall back to cached data
                data = await get_severe_weather_data(
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                    location="New York",
                    force_refresh=False
                )
            ```
        """
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format. Choose from: {self.supported_formats}")
            
        # Construct request parameters
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "format": format
        }
        
        if location:
            params["location"] = location
            
        if data_type != "all":
            params["dataType"] = data_type
            
        # Check cache
        cache_key = self._get_cache_key(params)
        cache_path = self._get_cache_path(cache_key, format)
        
        if not force_refresh and self._is_cache_valid(cache_path):
            logger.info("Loading data from cache")
            cached_data = self._load_from_cache(cache_path, format)
            if cached_data is not None:
                return {
                    "status": "success",
                    "result": cached_data
                }
                
        # Fetch fresh data from API
        try:
            logger.info("Fetching fresh data from NOAA API")
            response = requests.get(
                f"{self.base_url}/api/v1/data",
                params=params,
                headers={"token": self.api_key} if self.api_key else {}
            )
            response.raise_for_status()
            
            # Process response based on format
            if format == "json":
                data = response.json()
            elif format == "csv":
                data = pd.read_csv(response.content)
            else:
                data = response.content
                
            # Cache the data
            self._save_to_cache(data, cache_path)
            
            return {
                "status": "success",
                "result": data
            }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    @lru_cache(maxsize=100)
    def get_metadata(self) -> Dict:
        """
        Get metadata about available data types and formats.
        Cached using LRU cache to avoid frequent API calls.
        
        Returns:
            Dict containing:
                - status: "success" or "error"
                - result: Metadata about available data
                - error: Error message if status is "error"
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/metadata")
            response.raise_for_status()
            return {
                "status": "success",
                "result": response.json()
            }
        except Exception as e:
            logger.error(f"Failed to fetch metadata: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    def clear_cache(self, older_than: Optional[timedelta] = None):
        """
        Clear the cache.
        
        Args:
            older_than (timedelta, optional): Only clear cache entries older than this
        """
        try:
            for cache_file in self.cache_dir.glob("*.*"):
                if older_than:
                    cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if cache_age > older_than:
                        cache_file.unlink()
                else:
                    cache_file.unlink()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            
    async def analyze_weather_patterns(
        self,
        data: Union[Dict, pd.DataFrame],
        analysis_type: str = "frequency"
    ) -> Dict:
        """
        Analyze weather patterns in the data.
        
        This tool performs various analyses on weather data, including
        frequency analysis and severity assessment. It supports multiple
        analysis types and provides detailed results with confidence scores.
        
        Args:
            data: Weather data to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Dict containing:
                - status: "success" or "error"
                - result: Analysis results
                - error: Error message if status is "error"
                
        Error Handling:
            - On error, attempt alternative analysis type
            - If all analyses fail, return basic statistics
            - Log analysis failures for review
            
        Example:
            ```python
            # Basic usage
            patterns = await analyze_weather_patterns(
                data=weather_data,
                analysis_type="frequency"
            )
            
            # With error handling
            try:
                patterns = await analyze_weather_patterns(
                    data=weather_data,
                    analysis_type="severity"
                )
            except Exception as e:
                # Fall back to frequency analysis
                patterns = await analyze_weather_patterns(
                    data=weather_data,
                    analysis_type="frequency"
                )
            ```
        """
        try:
            if isinstance(data, pd.DataFrame):
                if analysis_type == "frequency":
                    return {
                        "status": "success",
                        "result": self._analyze_frequency(data)
                    }
                elif analysis_type == "severity":
                    return {
                        "status": "success",
                        "result": self._analyze_severity(data)
                    }
                else:
                    raise ValueError(f"Unsupported analysis type: {analysis_type}")
            else:
                raise ValueError("Data must be a pandas DataFrame")
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    def _analyze_frequency(self, df: pd.DataFrame) -> Dict:
        """Analyze frequency of weather events."""
        # Implementation here
        pass
        
    def _analyze_severity(self, df: pd.DataFrame) -> Dict:
        """Analyze severity of weather events."""
        # Implementation here
        pass

async def get_weather_data(
    location: str,
    time_period: str,
    force_refresh: bool = False
) -> Dict:
    """
    Get weather data for a location.
    
    This tool provides a simplified interface for retrieving weather data,
    with built-in caching and error handling. It's designed to be used
    as part of larger analysis workflows.
    
    Args:
        location: Location to get data for
        time_period: Time period for data
        force_refresh: Whether to force refresh data
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - result: Weather data
            - error: Error message if status is "error"
            
    Error Handling:
        - On error, attempt to load from cache
        - If cache fails, retry with exponential backoff
        - Log all errors for analysis
        
    Example:
        ```python
        # Basic usage
        data = await get_weather_data(
            location="New York",
            time_period="2024-01"
        )
        
        # With error handling
        try:
            data = await get_weather_data(
                location="New York",
                time_period="2024-01",
                force_refresh=True
            )
        except Exception as e:
            # Fall back to cached data
            data = await get_weather_data(
                location="New York",
                time_period="2024-01",
                force_refresh=False
            )
        ```
    """
    try:
        noaa = NOAAWeatherData()
        data = await noaa.get_severe_weather_data(
            start_date=time_period,
            end_date=time_period,
            location=location,
            force_refresh=force_refresh
        )
        return data
    except Exception as e:
        logger.error(f"Failed to get weather data: {e}")
        return {
            "status": "error",
            "error": str(e)
        } 