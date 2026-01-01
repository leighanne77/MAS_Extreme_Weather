"""
Data.gov MCP Server Integration for Pythia Multi-Agent System

This module provides access to Data.gov datasets including EPA, FEMA, NOAA, USGS,
and other federal agency data. It uses the Data.gov Catalog API directly.

Data.gov is the home of the U.S. Government's open data, providing access to
thousands of datasets from federal agencies.

No API key required - uses public Data.gov API.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

import requests

from .data_source import DataSource

logger = logging.getLogger(__name__)


class DataGovDataProvider(DataSource):
    """
    Data.gov Data Provider for accessing government datasets.
    
    Provides access to datasets from:
    - EPA (Environmental Protection Agency)
    - FEMA (Federal Emergency Management Agency)
    - NOAA (National Oceanic and Atmospheric Administration)
    - USGS (U.S. Geological Survey)
    - Census Bureau
    - Department of Energy
    - And many more federal agencies
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize Data.gov data provider.
        
        Args:
            cache_dir: Directory for caching data
        """
        super().__init__()
        self.base_url = "https://catalog.data.gov/api/3"
        self.cache_dir = Path(cache_dir) / "datagov"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = timedelta(hours=6)  # 6-hour cache for Data.gov data
    
    def _get_cache_key(self, params: dict) -> str:
        """Generate cache key from parameters."""
        import hashlib
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
    
    def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load data from cache."""
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None
    
    def _save_to_cache(self, data: Dict, cache_path: Path):
        """Save data to cache."""
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def package_search(
        self,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        rows: int = 10,
        start: int = 0,
        organization: Optional[str] = None,
        tags: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Search for packages (datasets) on Data.gov.
        
        Args:
            q: Search query text
            sort: Sort order (e.g., "score desc, name asc")
            rows: Number of results per page (default: 10)
            start: Starting offset for results (default: 0)
            organization: Filter by organization (e.g., "epa", "noaa", "usgs", "fema")
            tags: Filter by tags (list of tag names)
            force_refresh: Force refresh from API (bypass cache)
        
        Returns:
            Dict with search results
        """
        try:
            # Build request parameters
            params = {
                "rows": rows,
                "start": start
            }
            
            if q:
                params["q"] = q
            if sort:
                params["sort"] = sort
            if organization:
                params["fq"] = f"organization:{organization}"
            if tags:
                tag_filter = " OR ".join([f"tags:{tag}" for tag in tags])
                if "fq" in params:
                    params["fq"] += f" AND ({tag_filter})"
                else:
                    params["fq"] = tag_filter
            
            # Check cache
            cache_key = self._get_cache_key(params)
            cache_path = self._get_cache_path(cache_key)
            
            if not force_refresh and self._is_cache_valid(cache_path):
                logger.info("Loading Data.gov search results from cache")
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    return {
                        "status": "success",
                        "result": cached_data,
                        "source": "cache"
                    }
            
            # Fetch from API
            logger.info(f"Fetching Data.gov search results: {params}")
            response = requests.get(
                f"{self.base_url}/action/package_search",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the data
            self._save_to_cache(data, cache_path)
            
            return {
                "status": "success",
                "result": data,
                "source": "api",
                "count": data.get("result", {}).get("count", 0),
                "results": data.get("result", {}).get("results", [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Data.gov API request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "status": "error",
                "error": f"Invalid JSON response: {str(e)}"
            }
    
    def package_show(
        self,
        package_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get details for a specific package (dataset).
        
        Args:
            package_id: Package ID or name
            force_refresh: Force refresh from API (bypass cache)
        
        Returns:
            Dict with package details
        """
        try:
            # Check cache
            cache_key = self._get_cache_key({"action": "package_show", "id": package_id})
            cache_path = self._get_cache_path(cache_key)
            
            if not force_refresh and self._is_cache_valid(cache_path):
                logger.info("Loading Data.gov package details from cache")
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    return {
                        "status": "success",
                        "result": cached_data,
                        "source": "cache"
                    }
            
            # Fetch from API
            logger.info(f"Fetching Data.gov package details: {package_id}")
            response = requests.get(
                f"{self.base_url}/action/package_show",
                params={"id": package_id},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the data
            self._save_to_cache(data, cache_path)
            
            return {
                "status": "success",
                "result": data,
                "source": "api",
                "package": data.get("result", {})
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Data.gov API request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "status": "error",
                "error": f"Invalid JSON response: {str(e)}"
            }
    
    def group_list(
        self,
        order_by: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        all_fields: bool = False,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        List groups (organizations) on Data.gov.
        
        Args:
            order_by: Field to order by (e.g., "name", "package_count")
            limit: Maximum number of results (default: 20)
            offset: Offset for results (default: 0)
            all_fields: Return all fields (default: False)
            force_refresh: Force refresh from API (bypass cache)
        
        Returns:
            Dict with list of groups
        """
        try:
            # Build request parameters
            params = {
                "limit": limit,
                "offset": offset
            }
            
            if order_by:
                params["order_by"] = order_by
            if all_fields:
                params["all_fields"] = "true"
            
            # Check cache
            cache_key = self._get_cache_key(params)
            cache_path = self._get_cache_path(cache_key)
            
            if not force_refresh and self._is_cache_valid(cache_path):
                logger.info("Loading Data.gov groups from cache")
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    return {
                        "status": "success",
                        "result": cached_data,
                        "source": "cache"
                    }
            
            # Fetch from API
            logger.info(f"Fetching Data.gov groups: {params}")
            response = requests.get(
                f"{self.base_url}/action/group_list",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the data
            self._save_to_cache(data, cache_path)
            
            return {
                "status": "success",
                "result": data,
                "source": "api",
                "groups": data.get("result", [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Data.gov API request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "status": "error",
                "error": f"Invalid JSON response: {str(e)}"
            }
    
    def tag_list(
        self,
        query: Optional[str] = None,
        all_fields: bool = False,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        List tags on Data.gov.
        
        Args:
            query: Search query for tags
            all_fields: Return all fields (default: False)
            force_refresh: Force refresh from API (bypass cache)
        
        Returns:
            Dict with list of tags
        """
        try:
            # Build request parameters
            params = {}
            
            if query:
                params["query"] = query
            if all_fields:
                params["all_fields"] = "true"
            
            # Check cache
            cache_key = self._get_cache_key(params)
            cache_path = self._get_cache_path(cache_key)
            
            if not force_refresh and self._is_cache_valid(cache_path):
                logger.info("Loading Data.gov tags from cache")
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    return {
                        "status": "success",
                        "result": cached_data,
                        "source": "cache"
                    }
            
            # Fetch from API
            logger.info(f"Fetching Data.gov tags: {params}")
            response = requests.get(
                f"{self.base_url}/action/tag_list",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the data
            self._save_to_cache(data, cache_path)
            
            return {
                "status": "success",
                "result": data,
                "source": "api",
                "tags": data.get("result", [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Data.gov API request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "status": "error",
                "error": f"Invalid JSON response: {str(e)}"
            }
    
    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from Data.gov (async wrapper for DataSource interface).
        
        Args:
            **kwargs: Arguments for fetching data
                - action: "package_search", "package_show", "group_list", "tag_list"
                - Other arguments depend on the action
        
        Returns:
            Dict with fetched data
        """
        action = kwargs.get("action", "package_search")
        
        if action == "package_search":
            return self.package_search(
                q=kwargs.get("q"),
                sort=kwargs.get("sort"),
                rows=kwargs.get("rows", 10),
                start=kwargs.get("start", 0),
                organization=kwargs.get("organization"),
                tags=kwargs.get("tags"),
                force_refresh=kwargs.get("force_refresh", False)
            )
        elif action == "package_show":
            return self.package_show(
                package_id=kwargs.get("package_id") or kwargs.get("id"),
                force_refresh=kwargs.get("force_refresh", False)
            )
        elif action == "group_list":
            return self.group_list(
                order_by=kwargs.get("order_by"),
                limit=kwargs.get("limit", 20),
                offset=kwargs.get("offset", 0),
                all_fields=kwargs.get("all_fields", False),
                force_refresh=kwargs.get("force_refresh", False)
            )
        elif action == "tag_list":
            return self.tag_list(
                query=kwargs.get("query"),
                all_fields=kwargs.get("all_fields", False),
                force_refresh=kwargs.get("force_refresh", False)
            )
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}. Use: package_search, package_show, group_list, tag_list"
            }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the Data.gov data provider.
        
        Returns:
            Dict with metadata
        """
        return {
            "name": "Data.gov Data Provider",
            "description": "Access to government datasets from Data.gov (EPA, FEMA, NOAA, USGS, etc.)",
            "base_url": self.base_url,
            "cache_enabled": True,
            "cache_expiry_hours": self.cache_expiry.total_seconds() / 3600,
            "available_actions": [
                "package_search",
                "package_show",
                "group_list",
                "tag_list"
            ]
        }


# Convenience function for getting Data.gov data provider instance
def get_datagov_provider() -> DataGovDataProvider:
    """
    Get an instance of DataGovDataProvider.
    
    Returns:
        DataGovDataProvider instance
    """
    return DataGovDataProvider()




