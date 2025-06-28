#!/usr/bin/env python3
"""
Test script to verify all data files work correctly
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_data_files():
    """Test all data files to ensure they load correctly."""
    print("🧪 Testing Tool Data Files")
    print("=" * 40)
    
    try:
        from multi_agent_system.data.data_loader import get_data_loader
        
        # Get the data loader
        loader = get_data_loader()
        
        # Test nature-based solutions
        print("\n📊 Testing Nature-Based Solutions...")
        nbs_data = loader.load_nature_based_solutions()
        print(f"  ✅ Loaded {len(nbs_data.get('solutions', []))} solutions")
        
        # Test historical weather events
        print("\n🌪️ Testing Historical Weather Events...")
        hist_data = loader.load_historical_weather_events()
        print(f"  ✅ Loaded {len(hist_data.get('events', []))} events")
        
        # Test economic impact data
        print("\n💰 Testing Economic Impact Data...")
        econ_data = loader.load_economic_impact_data()
        print(f"  ✅ Loaded economic impact data with {len(econ_data.get('economic_impacts', {}))} impact types")
        
        # Test regional risk profiles
        print("\n🗺️ Testing Regional Risk Profiles...")
        regional_data = loader.load_regional_risk_profiles()
        print(f"  ✅ Loaded {len(regional_data.get('regions', {}))} regions")
        
        # Test data summary
        print("\n📋 Data Summary:")
        summary = loader.get_all_data_summary()
        print(f"  Nature-based solutions: {summary['nature_based_solutions']['count']}")
        print(f"  Historical events: {summary['historical_events']['count']}")
        print(f"  Regions: {summary['regions']['count']}")
        
        # Test specific queries
        print("\n🔍 Testing Specific Queries...")
        
        # Test solution search
        flood_solutions = loader.get_solutions_by_risk_type("flooding")
        print(f"  Flood solutions: {len(flood_solutions)}")
        
        # Test regional profile
        gulf_profile = loader.get_regional_profile("gulf_coast")
        if gulf_profile:
            print(f"  Gulf Coast risks: {len(gulf_profile.get('primary_risks', {}))}")
        
        # Test economic impacts
        hurricane_impacts = loader.get_economic_impact_by_event_type("hurricane")
        if hurricane_impacts:
            print(f"  Hurricane impact categories: {len(hurricane_impacts)}")
        
        print("\n✅ All data files loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing data files: {e}")
        return False

def show_data_examples():
    """Show examples of the data content."""
    print("\n📖 Data Examples:")
    print("=" * 30)
    
    try:
        from multi_agent_system.data.data_loader import get_data_loader
        loader = get_data_loader()
        
        # Show nature-based solution example
        print("\n🌿 Nature-Based Solution Example:")
        wetland_solution = loader.get_solution_by_id("wetland_restoration")
        if wetland_solution:
            print(f"  Name: {wetland_solution['name']}")
            print(f"  Risk Types: {', '.join(wetland_solution['risk_types'])}")
            print(f"  Benefits: {', '.join(wetland_solution['benefits'][:3])}...")
        
        # Show historical event example
        print("\n🌪️ Historical Event Example:")
        katrina_event = loader.get_historical_event_by_id("hurricane_katrina_2005")
        if katrina_event:
            print(f"  Name: {katrina_event['name']}")
            print(f"  Type: {katrina_event['type']}")
            print(f"  Damage Cost: ${katrina_event['impact']['damage_cost']:,}")
        
        # Show regional profile example
        print("\n🗺️ Regional Profile Example:")
        gulf_profile = loader.get_regional_profile("gulf_coast")
        if gulf_profile:
            print(f"  Region: {gulf_profile['name']}")
            print(f"  Primary Risks: {', '.join(gulf_profile['primary_risks'].keys())}")
            print(f"  Adaptation Priorities: {', '.join(gulf_profile['adaptation_priorities'][:3])}...")
        
        # Show economic impact example
        print("\n💰 Economic Impact Example:")
        hurricane_impacts = loader.get_economic_impact_by_event_type("hurricane")
        if hurricane_impacts:
            cat3 = hurricane_impacts.get("category_3", {})
            print(f"  Category 3 Hurricane:")
            print(f"    Damage Range: ${cat3['damage_range'][0]:,} - ${cat3['damage_range'][1]:,}")
            print(f"    Recovery Time: {cat3['recovery_time_days'][0]}-{cat3['recovery_time_days'][1]} days")
        
    except Exception as e:
        print(f"❌ Error showing examples: {e}")

def main():
    """Main test function."""
    print("🌍 Tool Data Files Test")
    print("=" * 50)
    
    # Test data files
    success = test_data_files()
    
    if success:
        # Show examples
        show_data_examples()
        
        print("\n🎉 All tests passed! The data files are ready to use.")
        print("\n📁 Available Data Files:")
        data_dir = Path("src/multi_agent_system/data")
        for file in data_dir.glob("*.json"):
            print(f"  • {file.name}")
        
        print("\n🚀 Next Steps:")
        print("  1. The data files are ready for the Tool system")
        print("  2. Run the demos to see the system in action")
        print("  3. Fix the architecture issue to run the full system")
        
    else:
        print("\n❌ Some tests failed. Please check the data files.")

if __name__ == "__main__":
    main() 