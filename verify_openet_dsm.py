#!/usr/bin/env python3
"""
Verify DataSourceManager can access OpenET API using the correct API key and endpoint.
"""
from src.multi_agent_system.data import DataSourceManager
import os
from dotenv import load_dotenv

load_dotenv()

# Example coordinates and date range (California Central Valley)
lon = -120.5
lat = 38.5
start_date = "2023-01-01"
end_date = "2023-01-31"

# Ensure API key is present
assert os.getenv("OPENET_API_KEY"), "OPENET_API_KEY not set in environment!"

# Get DataSourceManager instance
dsm = DataSourceManager()

# Call OpenET API via DataSourceManager
result = dsm.call_api_source(
    "openet_api",
    lon, lat, start_date, end_date, "ensemble", use_cache=False
)

print("OpenET API result status:", result.get("status"))
if result.get("status") == "SUCCESS":
    print("Sample data:", str(result.get("data"))[:500], "...")
else:
    print("Error:", result.get("error"))
