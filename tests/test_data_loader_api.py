#!/usr/bin/env python3
"""
Test script to verify API integrations in data_loader and key data modules
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest
from multi_agent_system.data.data_loader import DataLoader

def test_opportunity_zone_api():
    loader = DataLoader()
    try:
        # This should not raise, but may require API key
        data = loader.load_opportunity_zone_data()
        assert isinstance(data, dict)
        print("✅ Opportunity Zone API integration works")
    except Exception as e:
        print(f"❌ Opportunity Zone API integration error: {e}")
        assert False, f"Opportunity Zone API failed: {e}"

def test_noaa_ncei_api():
    loader = DataLoader()
    try:
        data = loader.load_noaa_ncei_data()
        assert isinstance(data, dict)
        print("✅ NOAA NCEI API integration works")
    except Exception as e:
        print(f"❌ NOAA NCEI API integration error: {e}")
        assert False, f"NOAA NCEI API failed: {e}"

def test_usgs_twl_api():
    loader = DataLoader()
    try:
        data = loader.load_usgs_twl_data()
        assert isinstance(data, dict)
        print("✅ USGS TWL API integration works")
    except Exception as e:
        print(f"❌ USGS TWL API integration error: {e}")
        assert False, f"USGS TWL API failed: {e}"
