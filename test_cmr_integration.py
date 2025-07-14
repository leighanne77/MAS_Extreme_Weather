#!/usr/bin/env python3
"""
Test script for CMR MCP Integration

This script tests the NASA Earthdata CMR integration using EDL token authentication.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from multi_agent_system.data.cmr_mcp import CMRDataProvider, initialize_cmr_provider

def test_cmr_authentication():
    """Test CMR authentication with EDL token"""
    print("Testing CMR Authentication...")
    
    # Get EDL token from environment
    edl_token = os.getenv('NASA_EARTHDATA_TOKEN')
    if not edl_token:
        print("❌ NASA_EARTHDATA_TOKEN not found in environment variables")
        print("Please set your EDL token in the .env file")
        return False
    
    try:
        # Initialize CMR provider
        cmr_provider = initialize_cmr_provider(edl_token)
        
        if cmr_provider._authenticated:
            print("✅ Successfully authenticated with NASA Earthdata")
            return True
        else:
            print("❌ Failed to authenticate with NASA Earthdata")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

def test_dataset_search():
    """Test dataset search functionality"""
    print("\nTesting Dataset Search...")
    
    try:
        cmr_provider = CMRDataProvider()
        
        # Test basic search
        print("Searching for climate datasets...")
        climate_datasets = cmr_provider.get_climate_datasets()
        
        if climate_datasets:
            print(f"✅ Found {len(climate_datasets)} climate datasets")
            for i, dataset in enumerate(climate_datasets[:3]):  # Show first 3
                print(f"  {i+1}. {dataset['short_name']} - {dataset['title']}")
        else:
            print("❌ No climate datasets found")
            return False
        
        # Test region-specific search
        print("\nSearching for Gulf Coast datasets...")
        gulf_datasets = cmr_provider.get_climate_datasets(region="Gulf Coast")
        
        if gulf_datasets:
            print(f"✅ Found {len(gulf_datasets)} Gulf Coast datasets")
        else:
            print("⚠️  No Gulf Coast specific datasets found (this is normal)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during dataset search: {e}")
        return False

def test_oceanographic_search():
    """Test oceanographic dataset search"""
    print("\nTesting Oceanographic Dataset Search...")
    
    try:
        cmr_provider = CMRDataProvider()
        
        ocean_datasets = cmr_provider.get_oceanographic_datasets()
        
        if ocean_datasets:
            print(f"✅ Found {len(ocean_datasets)} oceanographic datasets")
            for i, dataset in enumerate(ocean_datasets[:3]):  # Show first 3
                print(f"  {i+1}. {dataset['short_name']} - {dataset['title']}")
        else:
            print("❌ No oceanographic datasets found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during oceanographic search: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing CMR MCP Integration for Pythia")
    print("=" * 50)
    
    # Test authentication
    auth_success = test_cmr_authentication()
    
    if not auth_success:
        print("\n❌ Authentication failed. Please check your EDL token.")
        return
    
    # Test dataset search
    search_success = test_dataset_search()
    
    # Test oceanographic search
    ocean_success = test_oceanographic_search()
    
    print("\n" + "=" * 50)
    if auth_success and search_success and ocean_success:
        print("🎉 All tests passed! CMR integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 