
## Common Servers

### **NOAA CoastWatch Servers**

1. **ERD/CoastWatch West Coast Node**
   - **Name**: "ERD/CoastWatch West Coast Node" or "coastwatch"
   - **Short Name**: "CSWC"
   - **URL**: `https://coastwatch.pfeg.noaa.gov/erddap/`
   - **Use**: West Coast satellite and in-situ oceanographic data

2. **NOAA CoastWatch Central Operations**
   - **Name**: "NOAA CoastWatch Central Operations" or "coastwatch central"
   - **Short Name**: "NCCO"
   - **URL**: `https://coastwatch.noaa.gov/erddap/`
   - **Use**: Central operations data

3. **NOAA CoastWatch Great Lakes Node**
   - **Name**: "NOAA CoastWatch Great Lakes Node"
   - **URL**: `https://coastwatch.glerl.noaa.gov/erddap/`
   - **Use**: Great Lakes data

### **GCOOS (Gulf of Mexico) Servers**

1. **GCOOS Atmospheric and Oceanographic: Historical Data**
   - **Name**: "GCOOS" or "gcoos"
   - **Short Name**: "GCOOS-TAMU" or "GCOOS"
   - **URL**: `https://gcoos5.geos.tamu.edu/erddap/`
   - **Use**: Gulf of Mexico historical atmospheric and oceanographic data

2. **GCOOS Biological and Socioeconomics**
   - **Name**: "GCOOS Biological"
   - **URL**: `https://gcoos4.tamu.edu/erddap/`
   - **Use**: Gulf of Mexico biological and socioeconomic data

3. **NOAA IOOS GCOOS**
   - **Name**: "NOAA IOOS GCOOS"
   - **URL**: `https://erddap.gcoos.org/erddap/`
   - **Use**: IOOS GCOOS data

### **IOOS Servers**

1. **IOOS ERDDAP**
   - **Name**: "IOOS" or "ioos"
   - **Short Name**: "IOOS"
   - **URL**: `https://erddap.ioos.us/erddap/`
   - **Use**: Integrated Ocean Observing System data

---

## Usage Examples

### **Example 1: Search CoastWatch Server**

```python
from src.multi_agent_system.agents.tools import search_erddap_datasets_tool

# Using server name (recommended)
results = await search_erddap_datasets_tool(
    search_text="sea surface temperature",
    server_name="coastwatch",  # or "CSWC"
    min_lat=25.0,
    max_lat=35.0,
    min_lon=-90.0,
    max_lon=-80.0
)

# Or using full URL
results = await search_erddap_datasets_tool(
    search_text="sea surface temperature",
    server_url="https://coastwatch.pfeg.noaa.gov/erddap/",
    min_lat=25.0,
    max_lat=35.0,
    min_lon=-90.0,
    max_lon=-80.0
)
```

### **Example 2: Search GCOOS Server**

```python
# Using server name (recommended)
results = await search_erddap_datasets_tool(
    search_text="temperature",
    server_name="gcoos",  # or "GCOOS"
    min_lat=25.0,
    max_lat=30.0,
    min_lon=-90.0,
    max_lon=-80.0
)

# Or using full URL
results = await search_erddap_datasets_tool(
    search_text="temperature",
    server_url="https://gcoos5.geos.tamu.edu/erddap/",
    min_lat=25.0,
    max_lat=30.0,
    min_lon=-90.0,
    max_lon=-80.0
)
```

### **Example 3: Get Data from CoastWatch**

```python
from src.multi_agent_system.agents.tools import get_erddap_data_tool

# Using server name
data = await get_erddap_data_tool(
    dataset_id="erdMWchla8day",
    server_name="coastwatch",  # or "CSWC"
    variables=["chlorophyll", "time", "latitude", "longitude"],
    constraints={"time>=": "2024-01-01"}
)
```

### **Example 4: Get Data from GCOOS**

```python
# Using server name
data = await get_erddap_data_tool(
    dataset_id="gcoos_dataset_id",
    server_name="gcoos",  # or "GCOOS"
    variables=["temperature", "salinity"],
    constraints={"time>=": "2024-01-01"}
)
```

### **Example 5: Compare Data from Multiple Servers**

```python
# Get data from CoastWatch
coastwatch_data = await get_erddap_data_tool(
    dataset_id="dataset_id",
    server_name="coastwatch"
)

# Get data from GCOOS
gcoos_data = await get_erddap_data_tool(
    dataset_id="dataset_id",
    server_name="gcoos"
)

# Compare results
print(f"CoastWatch: {coastwatch_data['data']['row_count']} rows")
print(f"GCOOS: {gcoos_data['data']['row_count']} rows")
```

### **Example 6: List All Available Servers**

```python
from src.multi_agent_system.agents.tools import get_erddap_servers_tool

# Get all servers
servers_result = await get_erddap_servers_tool()

# Find specific servers
coastwatch_servers = [
    s for s in servers_result['data']['servers']
    if 'coastwatch' in s.get('name', '').lower()
]

gcoos_servers = [
    s for s in servers_result['data']['servers']
    if 'gcoos' in s.get('name', '').lower()
]

print(f"Found {len(coastwatch_servers)} CoastWatch servers")
print(f"Found {len(gcoos_servers)} GCOOS servers")
```

### **Example 7: Get Server URL by Name**

```python
from src.multi_agent_system.data.enhanced_data_sources import enhanced_data_manager

erddap_provider = enhanced_data_manager.sources["erddap"]

# Get server URL by name
coastwatch_url = erddap_provider.get_server_url("coastwatch")
gcoos_url = erddap_provider.get_server_url("gcoos")

print(f"CoastWatch URL: {coastwatch_url}")
print(f"GCOOS URL: {gcoos_url}")
```

---

## Helper Methods

### **Get Server by Name**

```python
from src.multi_agent_system.data.enhanced_data_sources import enhanced_data_manager

erddap_provider = enhanced_data_manager.sources["erddap"]

# Get server configuration
coastwatch = erddap_provider.get_server_by_name("coastwatch")
gcoos = erddap_provider.get_server_by_name("gcoos")

print(f"CoastWatch: {coastwatch['name']} - {coastwatch['url']}")
print(f"GCOOS: {gcoos['name']} - {gcoos['url']}")
```

### **Get Server URL**

```python
# Get URL by name or short_name
url = erddap_provider.get_server_url("coastwatch")  # Returns URL
url = erddap_provider.get_server_url("CSWC")  # Also works
url = erddap_provider.get_server_url("gcoos")  # Returns GCOOS URL
url = erddap_provider.get_server_url("GCOOS")  # Also works
```

---

## Best Practices

1. **Use server_name instead of server_url** - Easier to remember and less error-prone
2. **List servers first** - Use `get_erddap_servers_tool()` to see all available servers
3. **Check server availability** - Some servers may be temporarily unavailable
4. **Use appropriate servers for your region**:
   - **Gulf of Mexico**: Use GCOOS servers
   - **West Coast**: Use CoastWatch West Coast Node
   - **Great Lakes**: Use CoastWatch Great Lakes Node
   - **General**: Use IOOS or CoastWatch Central Operations

---

## Available Server Names

Common server names you can use:
- `"coastwatch"` or `"CSWC"` - NOAA CoastWatch West Coast
- `"gcoos"` or `"GCOOS"` - GCOOS Atmospheric and Oceanographic
- `"ioos"` or `"IOOS"` - IOOS ERDDAP
- `"UAF"` - NOAA UAF (Unified Access Framework)
- `"POLARWATCH"` - NOAA Polar Watch
- `"NCCO"` - NOAA CoastWatch Central Operations

Use `get_erddap_servers_tool()` to see the complete list of 63+ servers.
