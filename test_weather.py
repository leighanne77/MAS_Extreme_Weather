"""
Simple test script for the Weather Risk Analyzer.
"""

import os
from dotenv import load_dotenv
from multi_tool_agent.weather_risks import ClimateRiskAnalyzer

def test_risk_analyzer():
    """Test the climate risk analyzer functionality."""
    print("\n=== Testing Risk Analyzer ===")
    
    # Load API key from environment
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: OPENWEATHER_API_KEY not found in environment variables")
        return
    
    # Initialize the analyzer
    analyzer = ClimateRiskAnalyzer(api_key)
    
    # Test coordinates for New York City
    lat, lon = 40.7128, -74.0060
    
    try:
        # Get weather data
        weather_data = analyzer.get_weather_data(lat, lon)
        print("\nWeather Data:")
        print(f"Temperature: {weather_data.get('main', {}).get('temp')}°C")
        print(f"Humidity: {weather_data.get('main', {}).get('humidity')}%")
        print(f"Wind Speed: {weather_data.get('wind', {}).get('speed')} m/s")
        
        # Analyze risks
        risks = analyzer.analyze_risks(lat, lon)
        print("\nIdentified Risks:")
        for risk in risks:
            print(f"\nType: {risk['type']}")
            print(f"Severity: {risk['severity']}")
            print(f"Description: {risk['description']}")
            print("Recommendations:")
            for rec in risk['recommendations']:
                print(f"- {rec}")
                
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the test
    test_risk_analyzer() 