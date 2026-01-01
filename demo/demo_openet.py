"""
Demo script for OpenET API integration

This script demonstrates how to fetch evapotranspiration (ET) data from the OpenET API using the OpenETDataSource class.
"""

from src.multi_agent_system.data.openet_api import OpenETDataSource

if __name__ == "__main__":
    # Example coordinates (longitude, latitude) for Kansas
    lon = -100.0
    lat = 38.0
    start_date = "2022-01-01"
    end_date = "2022-12-31"
    source = "ensemble"  # or 'ssebop', 'disalexi', etc.

    openet = OpenETDataSource()
    result = openet.get_et(lon, lat, start_date, end_date, source)

    if result["status"] == "success":
        print("Evapotranspiration data:")
        print(result["data"])
    else:
        print("Error fetching ET data:", result["error"])
