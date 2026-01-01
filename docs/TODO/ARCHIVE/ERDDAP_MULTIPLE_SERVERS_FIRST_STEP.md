# ERDDAP Multiple Servers - First Step Guide

**Date Created**: December 15, 2025  
**Purpose**: Clear first step for using multiple ERDDAP servers in the Pythia system

---

## First Step: List Available ERDDAP Servers

**Before using any ERDDAP server, you should first discover what servers are available.**

### **Step 1: List All Available Servers**

Use the `get_erddap_servers_tool()` to see all 63+ pre-configured ERDDAP servers:

```python
from src.multi_agent_system.agents.tools import get_erddap_servers_tool

# List all available servers
servers_result = await get_erddap_servers_tool()

# The result will contain:
# {
#   "status": "success",
#   "data": {
#     "servers": [
#       {
#         "name": "ERD/CoastWatch West Coast Node",
#         "short_name": "CSWC",
#         "url": "https://coastwatch.pfeg.noaa.gov/erddap/",
#         "public": true
#       },
#       {
#         "name": "GCOOS Atmospheric and Oceanographic: Historical Data",
#         "short_name": "GCOOS-TAMU",
#         "url": "https://gcoos5.geos.tamu.edu/erddap/",
#         "public": true
#       },
#       ... (63+ more servers)
#     ],
#     "count": 63,
#     "total_servers": 63
#   }
# }
```

### **Step 2: Filter Servers by Region or Type**

Once you have the server list, filter to find servers relevant to your location:

```python
# Find servers for Gulf of Mexico
gcoos_servers = [
    s for s in servers_result['data']['servers']
    if 'gcoos' in s.get('name', '').lower() or 'gcoos' in s.get('short_name', '').lower()
]

# Find CoastWatch servers
coastwatch_servers = [
    s for s in servers_result['data']['servers']
    if 'coastwatch' in s.get('name', '').lower()
]

# Find servers for specific regions
# Example: Great Lakes
great_lakes_servers = [
    s for s in servers_result['data']['servers']
    if 'great lakes' in s.get('name', '').lower() or 'glerl' in s.get('url', '').lower()
]
```

### **Step 3: Choose Your Server**

Based on your location and data needs, select the appropriate server:

**For Gulf of Mexico (Mobile Bay, Alabama area):**
- **Recommended**: `"gcoos"` or `"GCOOS"` 
- **URL**: `https://gcoos5.geos.tamu.edu/erddap/`
- **Use**: Gulf of Mexico historical atmospheric and oceanographic data

**For West Coast:**
- **Recommended**: `"coastwatch"` or `"CSWC"`
- **URL**: `https://coastwatch.pfeg.noaa.gov/erddap/`
- **Use**: West Coast satellite and in-situ oceanographic data

**For General/IOOS:**
- **Recommended**: `"ioos"` or `"IOOS"`
- **URL**: `https://erddap.ioos.us/erddap/`
- **Use**: Integrated Ocean Observing System data

### **Step 4: Use Server Name in Your Queries**

Once you've identified your server, use the **server_name** parameter (recommended) instead of the full URL:

```python
from src.multi_agent_system.agents.tools import search_erddap_datasets_tool

# Using server name (RECOMMENDED - easier and less error-prone)
results = await search_erddap_datasets_tool(
    search_text="sea surface temperature",
    server_name="gcoos",  # Simple name, not full URL
    min_lat=25.0,
    max_lat=35.0,
    min_lon=-90.0,
    max_lon=-80.0
)
```

---

## Quick Reference: Common Server Names

| Server Name | Short Name | Use Case |
|------------|------------|----------|
| `"gcoos"` | `"GCOOS"` | Gulf of Mexico data |
| `"coastwatch"` | `"CSWC"` | West Coast data |
| `"ioos"` | `"IOOS"` | General IOOS data |
| `"NCCO"` | `"NCCO"` | CoastWatch Central Operations |
| `"UAF"` | `"UAF"` | NOAA Unified Access Framework |
| `"POLARWATCH"` | `"POLARWATCH"` | Polar regions data |

---

## Complete First Step Workflow

```python
# 1. List all servers
servers = await get_erddap_servers_tool()

# 2. Find relevant servers for your location
# Example: For Mobile Bay, Alabama (Gulf of Mexico)
gulf_servers = [s for s in servers['data']['servers'] 
                if 'gcoos' in s.get('name', '').lower()]

# 3. Use server name in your data queries
data = await search_erddap_datasets_tool(
    search_text="temperature",
    server_name="gcoos",  # Use the simple name
    min_lat=30.0,  # Mobile Bay approximate coordinates
    max_lat=31.0,
    min_lon=-88.5,
    max_lon=-87.5
)
```

---

## Why This First Step Matters

1. **Discover Available Data**: See what servers have data for your region
2. **Choose Best Server**: Select the server with most relevant data for your location
3. **Avoid Errors**: Using server names prevents URL typos
4. **Flexibility**: Easy to switch between servers for comparison

---

## Next Steps After Listing Servers

1. **Search Datasets**: Use `search_erddap_datasets_tool()` with your chosen server
2. **Get Dataset Info**: Use `get_erddap_dataset_info_tool()` to understand data structure
3. **Retrieve Data**: Use `get_erddap_data_tool()` to get actual data
4. **Compare Servers**: Query multiple servers to compare data coverage

---

## Reference

- **Full Guide**: `docs/TODO/2_ERDDAP_MULTIPLE_SERVERS_USAGE.md`
- **Server Config**: `dependencies/erddap2mcp/erddaps.json` (63+ servers)
- **Implementation**: `src/multi_agent_system/data/erddap_mcp.py`
- **Tools**: `src/multi_agent_system/agents/tools.py` (ERDDAP tools)

