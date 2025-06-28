#!/usr/bin/env python3
"""
Simple test script to verify data files work correctly
"""

import json
import os
from pathlib import Path

def test_json_files():
    """Test all JSON data files to ensure they load correctly."""
    print("🧪 Testing Tool JSON Data Files")
    print("=" * 45)
    
    data_dir = Path("src/multi_agent_system/data")
    json_files = list(data_dir.glob("*.json"))
    
    results = {}
    
    for json_file in json_files:
        print(f"\n📄 Testing {json_file.name}...")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Basic validation based on file type
            if "solutions" in data:
                count = len(data.get("solutions", []))
                print(f"  ✅ Loaded {count} nature-based solutions")
                results[json_file.name] = {"type": "nature_based_solutions", "count": count}
                
            elif "events" in data:
                count = len(data.get("events", []))
                print(f"  ✅ Loaded {count} historical weather events")
                results[json_file.name] = {"type": "historical_events", "count": count}
                
            elif "economic_impacts" in data:
                impact_types = len(data.get("economic_impacts", {}))
                print(f"  ✅ Loaded economic impact data with {impact_types} impact types")
                results[json_file.name] = {"type": "economic_impacts", "count": impact_types}
                
            elif "regions" in data:
                count = len(data.get("regions", {}))
                print(f"  ✅ Loaded {count} regional risk profiles")
                results[json_file.name] = {"type": "regional_profiles", "count": count}
                
            else:
                print(f"  ✅ Loaded JSON file (unknown structure)")
                results[json_file.name] = {"type": "unknown", "count": 0}
                
        except Exception as e:
            print(f"  ❌ Error loading {json_file.name}: {e}")
            results[json_file.name] = {"type": "error", "error": str(e)}
    
    return results

def show_data_summary(results):
    """Show a summary of the data files."""
    print("\n📊 Data Files Summary:")
    print("=" * 30)
    
    total_files = len(results)
    successful_files = sum(1 for r in results.values() if r["type"] != "error")
    
    print(f"Total JSON files: {total_files}")
    print(f"Successfully loaded: {successful_files}")
    print(f"Failed to load: {total_files - successful_files}")
    
    print("\n📁 File Details:")
    for filename, result in results.items():
        if result["type"] != "error":
            print(f"  • {filename}: {result['count']} items ({result['type']})")
        else:
            print(f"  • {filename}: ❌ {result['error']}")

def show_data_examples():
    """Show examples from the data files."""
    print("\n📖 Data Examples:")
    print("=" * 30)
    
    data_dir = Path("src/multi_agent_system/data")
    
    # Show nature-based solutions example
    nbs_file = data_dir / "nature_based_solutions.json"
    if nbs_file.exists():
        try:
            with open(nbs_file, 'r') as f:
                data = json.load(f)
            if data.get("solutions"):
                solution = data["solutions"][0]
                print(f"\n🌿 Nature-Based Solution Example:")
                print(f"  Name: {solution.get('name', 'N/A')}")
                print(f"  Risk Types: {', '.join(solution.get('risk_types', []))}")
                print(f"  Benefits: {', '.join(solution.get('benefits', [])[:3])}...")
        except Exception as e:
            print(f"❌ Error reading nature-based solutions: {e}")
    
    # Show historical events example
    hist_file = data_dir / "historical_weather_events.json"
    if hist_file.exists():
        try:
            with open(hist_file, 'r') as f:
                data = json.load(f)
            if data.get("events"):
                event = data["events"][0]
                print(f"\n🌪️ Historical Event Example:")
                print(f"  Name: {event.get('name', 'N/A')}")
                print(f"  Type: {event.get('type', 'N/A')}")
                print(f"  Date: {event.get('date', 'N/A')}")
        except Exception as e:
            print(f"❌ Error reading historical events: {e}")
    
    # Show regional profiles example
    regional_file = data_dir / "regional_risk_profiles.json"
    if regional_file.exists():
        try:
            with open(regional_file, 'r') as f:
                data = json.load(f)
            if data.get("regions"):
                region_name = list(data["regions"].keys())[0]
                region = data["regions"][region_name]
                print(f"\n🗺️ Regional Profile Example:")
                print(f"  Region: {region.get('name', 'N/A')}")
                print(f"  Primary Risks: {', '.join(region.get('primary_risks', {}).keys())}")
        except Exception as e:
            print(f"❌ Error reading regional profiles: {e}")

def main():
    """Main test function."""
    print("🌍 Tool Data Files - Simple Test")
    print("=" * 50)
    
    # Test JSON files
    results = test_json_files()
    
    # Show summary
    show_data_summary(results)
    
    # Show examples
    show_data_examples()
    
    # Check if all files loaded successfully
    failed_files = [f for f, r in results.items() if r["type"] == "error"]
    
    if not failed_files:
        print("\n🎉 All data files loaded successfully!")
        print("\n📁 Available Data Files:")
        data_dir = Path("src/multi_agent_system/data")
        for file in data_dir.glob("*.json"):
            print(f"  • {file.name}")
        
        print("\n🚀 Next Steps:")
        print("  1. ✅ Data files are ready for the Tool system")
        print("  2. Run: python demo.py to see the system overview")
        print("  3. Run: python simple_example.py for a working example")
        print("  4. Fix the architecture issue to run the full web interface")
        
    else:
        print(f"\n❌ {len(failed_files)} files failed to load:")
        for file in failed_files:
            print(f"  • {file}")

if __name__ == "__main__":
    main() 