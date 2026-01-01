# USGS Real-time GeoJSON Feed Integration for Earthquake Data

**Date Created**: December 14, 2025  
**Status**: Recommendations Only (No Changes Made)  
**Source**: [USGS Earthquake Hazards Program - Real-time Feeds](https://earthquake.usgs.gov/earthquakes/feed/)

---

## Overview

USGS recommends using **Real-time GeoJSON Feeds** for earthquake data instead of API endpoints. These feeds provide better performance and availability for automated applications.

**Key Benefits**:
- ✅ **No API Key Required** - Free public access
- ✅ **Better Performance** - Optimized for automated applications
- ✅ **Real-time Updates** - Regularly updated feeds
- ✅ **Simple Integration** - Standard GeoJSON format
- ✅ **Multiple Time Ranges** - Past hour, day, week, month
- ✅ **Magnitude Filtering** - Pre-filtered by magnitude thresholds

---

## Available GeoJSON Feeds

### **Time-Based Feeds**:
- **Past Hour**: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson`
- **Past Day**: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`
- **Past 7 Days**: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson`
- **Past 30 Days**: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson`

### **Magnitude-Filtered Feeds**:
- **Magnitude 1.0+**: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_hour.geojson` (and `_day`, `_week`, `_month`)
- **Magnitude 2.5+**: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson` (and `_day`, `_week`, `_month`)
- **Magnitude 4.5+**: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson` (and `_day`, `_week`, `_month`)
- **Significant Earthquakes**: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson` (and `_day`, `_week`, `_month`)

---

## Recommended Implementation Approach

### **Option A: Direct GeoJSON Feed Integration (Recommended)**

Instead of using the USGS Quakes MCP Server, create a direct GeoJSON feed integration that follows existing patterns in the codebase.

#### **1. Create USGS Earthquake Data Source**

**File**: `src/multi_agent_system/data/usgs_earthquake_data.py`

**Implementation Pattern**: Follow the pattern used in `NOAAWeatherData` and `NOAASWDISource` classes.

```python
"""
USGS Real-time Earthquake Data Integration

Uses USGS Real-time GeoJSON Feeds for earthquake data.
Recommended by USGS for automated applications.
"""

import json
import logging
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class USGSEarthquakeData:
    """
    USGS Real-time Earthquake Data handler using GeoJSON feeds.
    
    Uses USGS recommended Real-time GeoJSON Feeds for better performance
    and availability. No API key required.
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize USGS Earthquake Data handler.
        
        Args:
            cache_dir: Directory for caching data
        """
        self.base_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary"
        self.cache_dir = Path(cache_dir) / "usgs_earthquake"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = timedelta(hours=1)  # Cache for 1 hour (feeds update frequently)
    
    def get_earthquake_feed_url(
        self,
        time_range: str = "day",
        min_magnitude: Optional[float] = None
    ) -> str:
        """
        Get the appropriate GeoJSON feed URL.
        
        Args:
            time_range: "hour", "day", "week", or "month"
            min_magnitude: Minimum magnitude (1.0, 2.5, 4.5) or None for all
        
        Returns:
            GeoJSON feed URL
        """
        if min_magnitude:
            # Use magnitude-filtered feed
            if min_magnitude >= 4.5:
                magnitude_str = "4.5"
            elif min_magnitude >= 2.5:
                magnitude_str = "2.5"
            elif min_magnitude >= 1.0:
                magnitude_str = "1.0"
            else:
                magnitude_str = None
        else:
            magnitude_str = None
        
        if magnitude_str:
            return f"{self.base_url}/{magnitude_str}_{time_range}.geojson"
        else:
            return f"{self.base_url}/all_{time_range}.geojson"
    
    async def get_earthquake_data(
        self,
        time_range: str = "day",
        min_magnitude: Optional[float] = None,
        location: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get earthquake data from USGS GeoJSON feed.
        
        Args:
            time_range: "hour", "day", "week", or "month"
            min_magnitude: Minimum magnitude filter (optional)
            location: Location filter (optional - filters results after fetching)
            force_refresh: Force refresh from API (bypass cache)
        
        Returns:
            Dict containing:
                - status: "success" or "error"
                - result: GeoJSON earthquake data
                - error: Error message if status is "error"
        """
        try:
            # Get feed URL
            feed_url = self.get_earthquake_feed_url(time_range, min_magnitude)
            
            # Check cache
            cache_key = f"usgs_quake_{time_range}_{min_magnitude or 'all'}"
            cache_path = self.cache_dir / f"{cache_key}.geojson"
            
            if not force_refresh and self._is_cache_valid(cache_path):
                logger.info("Loading earthquake data from cache")
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    return {
                        "status": "success",
                        "result": cached_data,
                        "source": "cache"
                    }
            
            # Fetch from GeoJSON feed
            logger.info(f"Fetching earthquake data from USGS GeoJSON feed: {feed_url}")
            response = requests.get(feed_url, timeout=30)
            response.raise_for_status()
            
            # Parse GeoJSON
            geojson_data = response.json()
            
            # Apply location filter if specified
            if location:
                geojson_data = self._filter_by_location(geojson_data, location)
            
            # Cache the data
            self._save_to_cache(geojson_data, cache_path)
            
            return {
                "status": "success",
                "result": geojson_data,
                "source": "api",
                "feed_url": feed_url,
                "count": len(geojson_data.get("features", []))
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"USGS GeoJSON feed request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GeoJSON: {e}")
            return {
                "status": "error",
                "error": f"Invalid GeoJSON format: {str(e)}"
            }
    
    def _filter_by_location(self, geojson_data: Dict, location: str) -> Dict:
        """
        Filter GeoJSON features by location (basic implementation).
        
        Args:
            geojson_data: GeoJSON data from USGS feed
            location: Location string to filter by
        
        Returns:
            Filtered GeoJSON data
        """
        # TODO: Implement location-based filtering
        # Could use geocoding to get coordinates, then filter by distance
        # For now, return all data
        return geojson_data
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is valid."""
        if not cache_path.exists():
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return file_age < self.cache_expiry
    
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
    
    def get_earthquake_summary(
        self,
        time_range: str = "day",
        min_magnitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics for earthquakes.
        
        Args:
            time_range: "hour", "day", "week", or "month"
            min_magnitude: Minimum magnitude filter
        
        Returns:
            Summary statistics
        """
        data = self.get_earthquake_data(time_range, min_magnitude)
        
        if data["status"] != "success":
            return data
        
        features = data["result"].get("features", [])
        
        if not features:
            return {
                "status": "success",
                "summary": {
                    "count": 0,
                    "time_range": time_range,
                    "min_magnitude": min_magnitude
                }
            }
        
        magnitudes = [
            f["properties"].get("mag", 0)
            for f in features
            if f["properties"].get("mag") is not None
        ]
        
        return {
            "status": "success",
            "summary": {
                "count": len(features),
                "time_range": time_range,
                "min_magnitude": min_magnitude,
                "max_magnitude": max(magnitudes) if magnitudes else None,
                "avg_magnitude": sum(magnitudes) / len(magnitudes) if magnitudes else None,
                "latest_earthquake": features[0]["properties"] if features else None
            }
        }
```

#### **2. Integration with Enhanced Data Sources**

**Option**: Add to `InfrastructureData` class in `enhanced_data_sources.py`:

```python
# In InfrastructureData class
async def get_earthquake_risk_data(self, location: str) -> dict[str, Any]:
    """
    Get earthquake risk data for a location.
    
    Uses USGS Real-time GeoJSON Feeds (recommended approach).
    """
    from .usgs_earthquake_data import USGSEarthquakeData
    
    earthquake_data = USGSEarthquakeData()
    
    # Get past 30 days of significant earthquakes (magnitude 2.5+)
    data = await earthquake_data.get_earthquake_data(
        time_range="month",
        min_magnitude=2.5,
        location=location
    )
    
    return data
```

#### **3. Add to Agent Tools**

**File**: `src/multi_agent_system/agents/tools.py`

Add earthquake data tool:

```python
async def get_usgs_earthquake_data(
    time_range: str = "day",
    min_magnitude: Optional[float] = None,
    location: Optional[str] = None
) -> dict:
    """
    Get USGS earthquake data from Real-time GeoJSON feeds.
    
    This uses USGS recommended Real-time GeoJSON Feeds for better
    performance and availability. No API key required.
    
    Args:
        time_range: "hour", "day", "week", or "month"
        min_magnitude: Minimum magnitude (1.0, 2.5, 4.5) or None for all
        location: Optional location filter
    
    Returns:
        GeoJSON earthquake data
    """
    from ..data.usgs_earthquake_data import USGSEarthquakeData
    
    earthquake_data = USGSEarthquakeData()
    return await earthquake_data.get_earthquake_data(
        time_range=time_range,
        min_magnitude=min_magnitude,
        location=location
    )
```

---

## Updated Credentials Requirements

### **USGS_QUAKE_API_KEY - NOT NEEDED** ✅

Since we're using the Real-time GeoJSON Feeds (which don't require an API key), **`USGS_QUAKE_API_KEY` is no longer needed**.

### **USGS_WATER_API_KEY - STILL NEEDED** ⚠️

The water data MCP server still requires an API key, so `USGS_WATER_API_KEY` is still needed.

---

## Advantages of GeoJSON Feed Approach

1. **No API Key Required** - Simplifies setup and maintenance
2. **Better Performance** - Optimized feeds for automated applications
3. **Real-time Updates** - Feeds are updated regularly
4. **Simple Integration** - Standard GeoJSON format, easy to parse
5. **Multiple Options** - Time ranges and magnitude filters available
6. **Recommended by USGS** - Official recommendation for automated apps
7. **No Rate Limits** - Public feeds with no authentication overhead

---

## Comparison: GeoJSON Feed vs. MCP Server

| Feature | GeoJSON Feed (Recommended) | MCP Server |
|---------|---------------------------|------------|
| **API Key Required** | ❌ No | ✅ Yes (`USGS_QUAKE_API_KEY`) |
| **Performance** | ✅ Optimized for automation | ⚠️ Standard |
| **Setup Complexity** | ✅ Simple (direct HTTP) | ⚠️ Requires MCP server setup |
| **Real-time Updates** | ✅ Yes | ✅ Yes |
| **USGS Recommendation** | ✅ Recommended | ⚠️ Alternative |
| **Maintenance** | ✅ Low (no server to manage) | ⚠️ Medium (server updates) |

---

## Implementation Recommendations

### **Recommended Approach**:
1. ✅ **Use GeoJSON Feeds** for earthquake data (no API key needed)
2. ✅ **Create `usgs_earthquake_data.py`** following existing patterns
3. ✅ **Add to `InfrastructureData`** class or create standalone data source
4. ✅ **Add agent tool** for earthquake data access
5. ❌ **Skip USGS Quakes MCP Server** - Not needed with GeoJSON feeds
6. ❌ **Skip `USGS_QUAKE_API_KEY`** - Not needed for GeoJSON feeds

### **Files to Create/Update**:
1. **Create**: `src/multi_agent_system/data/usgs_earthquake_data.py`
2. **Update**: `src/multi_agent_system/data/enhanced_data_sources.py` (add earthquake method to `InfrastructureData`)
3. **Update**: `src/multi_agent_system/agents/tools.py` (add earthquake data tool)
4. **Update**: Documentation to reflect GeoJSON feed approach

---

## Example Usage

```python
from src.multi_agent_system.data.usgs_earthquake_data import USGSEarthquakeData

# Initialize
earthquake_data = USGSEarthquakeData()

# Get past day of all earthquakes
data = await earthquake_data.get_earthquake_data(time_range="day")

# Get past week of significant earthquakes (magnitude 2.5+)
significant = await earthquake_data.get_earthquake_data(
    time_range="week",
    min_magnitude=2.5
)

# Get summary statistics
summary = earthquake_data.get_earthquake_summary(
    time_range="month",
    min_magnitude=2.5
)
```

---

## References

- **USGS Real-time GeoJSON Feeds**: [https://earthquake.usgs.gov/earthquakes/feed/](https://earthquake.usgs.gov/earthquakes/feed/)
- **USGS Earthquake API Documentation**: [https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)
- **GeoJSON Specification**: [https://geojson.org/](https://geojson.org/)

---

## Change Log

### **December 14, 2025**
- **Initial Creation**: Recommendations for using USGS Real-time GeoJSON Feeds instead of MCP server
- **Key Finding**: No API key required for GeoJSON feeds (simplifies setup)
- **Implementation Pattern**: Follows existing `NOAAWeatherData` pattern for consistency
- **Credentials Update**: `USGS_QUAKE_API_KEY` not needed when using GeoJSON feeds

