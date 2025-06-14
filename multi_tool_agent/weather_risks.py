"""
Weather risk analysis module that uses real-time weather data and standardized definitions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional
from .risk_definitions import get_consensus_thresholds, severity_levels

class ClimateRiskAnalyzer:
    """A comprehensive climate risk analysis tool that uses real-time weather data and standardized definitions.

    This class analyzes various climate risks including extreme heat, flooding, wildfire, and extreme storms
    using data from OpenWeather API and comparing it against thresholds defined by authoritative sources
    (FEMA, WHO, NOAA, ISO).

    Attributes:
        api_key (str): OpenWeatherMap API key for accessing weather data
        base_url (str): Base URL for OpenWeather API
        thresholds (Dict): Risk thresholds from authoritative sources
    """

    def __init__(self, api_key: str):
        """Initialize the ClimateRiskAnalyzer with an OpenWeatherMap API key.
        
        Args:
            api_key (str): OpenWeatherMap API key for accessing weather data.
                         Must be a valid API key from OpenWeatherMap.

        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("OpenWeatherMap API key is required")
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.thresholds = get_consensus_thresholds()
        
    def get_weather_data(self, lat: float, lon: float) -> Dict:
        """Fetch current weather data for a location from OpenWeather API.
        
        Args:
            lat (float): Latitude of the location (-90 to 90)
            lon (float): Longitude of the location (-180 to 180)
            
        Returns:
            Dict: Weather data including temperature, humidity, wind speed, and precipitation
            
        Raises:
            ValueError: If latitude or longitude are out of valid ranges
            requests.RequestException: If API request fails
        """
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to fetch weather data: {str(e)}")
    
    def analyze_risks(self, lat: float, lon: float) -> List[Dict]:
        """Analyze climate-related risks for a location using standardized definitions.
        
        This method analyzes multiple risk types:
        - Extreme Heat: Based on temperature thresholds
        - Flooding: Based on rainfall amounts
        - Wildfire: Based on temperature, humidity, and wind speed
        - Extreme Storms: Based on weather conditions and wind speed
        
        Args:
            lat (float): Latitude of the location (-90 to 90)
            lon (float): Longitude of the location (-180 to 180)
            
        Returns:
            List[Dict]: List of identified risks, each containing:
                - type (str): Risk type (e.g., "Extreme Heat", "Flooding")
                - severity (str): Risk severity ("High" or "Medium")
                - description (str): Detailed description of the risk
                - sources (List[str]): Authoritative sources for the risk assessment
                - recommendations (List[str]): Actionable recommendations
                
        Raises:
            ValueError: If latitude or longitude are invalid
            requests.RequestException: If weather data cannot be retrieved
        """
        try:
            weather_data = self.get_weather_data(lat, lon)
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to analyze risks: {str(e)}")

        risks = []
        
        # Extract weather parameters with error handling
        try:
            temp = weather_data.get("main", {}).get("temp")
            humidity = weather_data.get("main", {}).get("humidity")
            wind_speed = weather_data.get("wind", {}).get("speed")
            rain_1h = weather_data.get("rain", {}).get("1h", 0)
            weather_conditions = weather_data.get("weather", [])
        except (KeyError, AttributeError) as e:
            raise ValueError(f"Invalid weather data format: {str(e)}")

        # 1. Extreme Heat Risk (based on FEMA, WHO, and ISO standards)
        if temp is not None:
            heat_thresholds = self.thresholds["extreme_heat"]
            if temp > heat_thresholds["high"]["temperature"]:
                risks.append({
                    "type": "Extreme Heat",
                    "severity": "High",
                    "description": f"Extreme heat conditions detected ({temp}°C)",
                    "sources": heat_thresholds["high"]["sources"],
                    "recommendations": [
                        "Stay hydrated and avoid outdoor activities during peak hours",
                        "Check on vulnerable individuals",
                        "Use air conditioning or cooling centers if available",
                        "Monitor local heat advisories"
                    ]
                })
            elif temp > heat_thresholds["medium"]["temperature"]:
                risks.append({
                    "type": "Extreme Heat",
                    "severity": "Medium",
                    "description": f"High temperature conditions detected ({temp}°C)",
                    "sources": heat_thresholds["medium"]["sources"],
                    "recommendations": [
                        "Stay hydrated",
                        "Limit outdoor activities during peak hours",
                        "Monitor local weather updates"
                    ]
                })
        
        # 2. Flooding Risk (based on FEMA and ISO standards)
        if rain_1h > 0:
            flood_thresholds = self.thresholds["flooding"]
            if rain_1h > flood_thresholds["high"]["rainfall_1h"]:
                risks.append({
                    "type": "Flooding",
                    "severity": "High",
                    "description": f"Extreme rainfall detected ({rain_1h}mm in the last hour)",
                    "sources": flood_thresholds["high"]["sources"],
                    "recommendations": [
                        "Move to higher ground if in a flood-prone area",
                        "Avoid driving through flooded areas",
                        "Stay informed about local flood warnings",
                        "Follow evacuation orders if issued"
                    ]
                })
            elif rain_1h > flood_thresholds["medium"]["rainfall_1h"]:
                risks.append({
                    "type": "Flooding",
                    "severity": "Medium",
                    "description": f"Heavy rainfall detected ({rain_1h}mm in the last hour)",
                    "sources": flood_thresholds["medium"]["sources"],
                    "recommendations": [
                        "Be cautious in low-lying areas",
                        "Monitor local weather updates",
                        "Prepare for potential flooding"
                    ]
                })
        
        # 3. Wildfire Risk (based on FEMA and ISO standards)
        if temp is not None and humidity is not None and wind_speed is not None:
            wildfire_thresholds = self.thresholds["wildfire"]
            if (temp > wildfire_thresholds["high"]["temperature"] and 
                humidity < wildfire_thresholds["high"]["humidity"] and 
                wind_speed > wildfire_thresholds["high"]["wind_speed"]):
                risks.append({
                    "type": "Wildfire",
                    "severity": "High",
                    "description": f"High wildfire risk conditions: High temperature ({temp}°C), low humidity ({humidity}%), and strong winds ({wind_speed} m/s)",
                    "sources": wildfire_thresholds["high"]["sources"],
                    "recommendations": [
                        "Avoid outdoor burning",
                        "Be prepared for potential evacuation",
                        "Monitor local fire warnings",
                        "Have an evacuation plan ready"
                    ]
                })
            elif (temp > wildfire_thresholds["medium"]["temperature"] and 
                  humidity < wildfire_thresholds["medium"]["humidity"] and 
                  wind_speed > wildfire_thresholds["medium"]["wind_speed"]):
                risks.append({
                    "type": "Wildfire",
                    "severity": "Medium",
                    "description": f"Moderate wildfire risk conditions: Elevated temperature ({temp}°C), low humidity ({humidity}%), and moderate winds ({wind_speed} m/s)",
                    "sources": wildfire_thresholds["medium"]["sources"],
                    "recommendations": [
                        "Exercise caution with outdoor fires",
                        "Stay informed about local fire conditions",
                        "Prepare emergency supplies"
                    ]
                })
        
        # 4. Extreme Storms Risk (based on NOAA and ISO standards)
        storm_thresholds = self.thresholds["extreme_storms"]
        for condition in weather_conditions:
            main = condition.get("main", "").lower()
            if "thunderstorm" in main:
                risks.append({
                    "type": "Extreme Storms",
                    "severity": "High",
                    "description": "Thunderstorm conditions detected",
                    "sources": storm_thresholds["high"]["sources"],
                    "recommendations": [
                        "Seek shelter immediately",
                        "Stay away from windows and electrical equipment",
                        "Monitor local storm warnings",
                        "Have emergency supplies ready"
                    ]
                })
            elif wind_speed is not None and wind_speed > storm_thresholds["high"]["wind_speed"]:
                risks.append({
                    "type": "Extreme Storms",
                    "severity": "High",
                    "description": f"Strong wind conditions detected ({wind_speed} m/s)",
                    "sources": storm_thresholds["high"]["sources"],
                    "recommendations": [
                        "Secure outdoor objects",
                        "Stay indoors if possible",
                        "Be cautious of falling debris",
                        "Monitor local weather updates"
                    ]
                })
            elif wind_speed is not None and wind_speed > storm_thresholds["medium"]["wind_speed"]:
                risks.append({
                    "type": "Extreme Storms",
                    "severity": "Medium",
                    "description": f"Moderate wind conditions detected ({wind_speed} m/s)",
                    "sources": storm_thresholds["medium"]["sources"],
                    "recommendations": [
                        "Secure loose outdoor items",
                        "Stay informed about weather conditions",
                        "Prepare for potential power outages"
                    ]
                })
        
        return risks

def main():
    # Example usage
    api_key = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key
    analyzer = ClimateRiskAnalyzer(api_key)
    
    # Example coordinates (New York City)
    lat, lon = 40.7128, -74.0060
    
    risks = analyzer.analyze_risks(lat, lon)
    
    print(f"Climate-related risks for location (lat: {lat}, lon: {lon}):")
    for risk in risks:
        print(f"\nRisk Type: {risk['type']}")
        print(f"Severity: {risk['severity']}")
        print(f"Description: {risk['description']}")
        print(f"Sources: {', '.join(risk['sources'])}")
        print("Recommendations:")
        for rec in risk['recommendations']:
            print(f"- {rec}")

if __name__ == "__main__":
    main() 