"""
Weather risk analysis module that uses both OpenWeather API and NOAA data sources.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional, Union
import logging
from .weather_data import NOAAWeatherData, get_weather_data
from .risk_definitions import get_consensus_thresholds, severity_levels

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateRiskAnalyzer:
    """A comprehensive climate risk analysis tool that uses both OpenWeather API and NOAA data.

    This class analyzes various climate risks including extreme heat, flooding, wildfire, and extreme storms
    using data from both OpenWeather API and NOAA's Severe Weather Data Inventory (SWDI), comparing against
    thresholds defined by authoritative sources (FEMA, WHO, NOAA, ISO).

    Attributes:
        openweather_api_key (str): OpenWeatherMap API key
        noaa_data (NOAAWeatherData): NOAA weather data handler
        thresholds (Dict): Risk thresholds from authoritative sources
    """

    def __init__(self, openweather_api_key: str, noaa_api_key: Optional[str] = None):
        """Initialize the ClimateRiskAnalyzer with both data sources.
        
        Args:
            openweather_api_key (str): OpenWeatherMap API key for current weather data
            noaa_api_key (str, optional): API key for NOAA services
        """
        if not openweather_api_key:
            raise ValueError("OpenWeatherMap API key is required")
            
        self.openweather_api_key = openweather_api_key
        self.noaa_data = NOAAWeatherData(api_key=noaa_api_key)
        self.thresholds = get_consensus_thresholds()
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    async def get_weather_data(self, lat: float, lon: float) -> Dict:
        """Fetch current weather data from both sources.
        
        Args:
            lat (float): Latitude of the location (-90 to 90)
            lon (float): Longitude of the location (-180 to 180)
            
        Returns:
            Dict: Combined weather data from both sources
            
        Raises:
            ValueError: If latitude or longitude are out of valid ranges
        """
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        # Get current date and previous day for data range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        try:
            # 1. Get OpenWeather current data
            openweather_data = await self._get_openweather_data(lat, lon)
            
            # 2. Get NOAA severe weather data
            noaa_data = await self.noaa_data.get_severe_weather_data(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                location=f"{lat},{lon}",
                data_type="all",
                format="json"
            )
            
            if noaa_data["status"] == "error":
                logger.warning(f"Failed to fetch NOAA data: {noaa_data.get('error')}")
                noaa_data = {"result": {}}
            
            # 3. Get basic weather data as additional source
            basic_data = await get_weather_data(
                location=f"{lat},{lon}",
                time_period=end_date.strftime("%Y-%m"),
                force_refresh=False
            )
            
            if basic_data["status"] == "error":
                logger.warning(f"Failed to fetch basic weather data: {basic_data.get('error')}")
                basic_data = {"result": {}}
                
            # Combine all data sources
            return {
                "current_weather": openweather_data,
                "severe_weather": noaa_data["result"],
                "basic_weather": basic_data["result"]
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            raise

    async def _get_openweather_data(self, lat: float, lon: float) -> Dict:
        """Fetch current weather data from OpenWeather API."""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.openweather_api_key,
            "units": "metric"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"OpenWeather API error: {str(e)}")
            raise

    async def analyze_risks(self, lat: float, lon: float) -> List[Dict]:
        """Analyze climate-related risks using combined data sources.
        
        This method analyzes multiple risk types using data from both OpenWeather and NOAA:
        - Extreme Heat: Based on temperature thresholds and frequency of extreme heat events
        - Flooding: Based on rainfall amounts and frequency of 100-year flood events
        - Wildfire: Based on temperature, humidity, and wind speed
        - Extreme Storms: Based on weather conditions and wind speed
        
        Args:
            lat (float): Latitude of the location (-90 to 90)
            lon (float): Longitude of the location (-180 to 180)
            
        Returns:
            List[Dict]: List of identified risks with severity and recommendations
        """
        try:
            weather_data = await self.get_weather_data(lat, lon)
        except Exception as e:
            raise ValueError(f"Failed to analyze risks: {str(e)}")

        risks = []
        
        # Extract weather parameters from combined data
        try:
            current_weather = weather_data["current_weather"]
            severe_weather = weather_data["severe_weather"]
            basic_weather = weather_data["basic_weather"]
            
            # Use OpenWeather data for current conditions
            temp = current_weather.get("main", {}).get("temp")
            humidity = current_weather.get("main", {}).get("humidity")
            wind_speed = current_weather.get("wind", {}).get("speed")
            rain_1h = current_weather.get("rain", {}).get("1h", 0)
            weather_conditions = current_weather.get("weather", [])
            
            # Get historical data for frequency analysis
            historical_data = await self._get_historical_data(lat, lon)
            
        except (KeyError, AttributeError) as e:
            raise ValueError(f"Invalid weather data format: {str(e)}")

        # 1. Extreme Heat Risk (based on FEMA, WHO, and ISO standards)
        if temp is not None:
            heat_thresholds = self.thresholds["extreme_heat"]
            # Check for frequent extreme heat events using NOAA data
            frequent_extreme_heat = await self._check_frequent_extreme_heat(historical_data)
            if frequent_extreme_heat:
                risks.append({
                    "type": "Extreme Heat",
                    "severity": "Super Extreme",
                    "description": "Frequent extreme heat events detected in the past five years",
                    "sources": heat_thresholds["high"]["sources"],
                    "recommendations": [
                        "Immediate action required: Stay indoors, use air conditioning, and check on vulnerable individuals",
                        "Contact local emergency services if necessary",
                        "Review and update heat preparedness plans",
                        "Consider long-term heat mitigation strategies"
                    ]
                })
            elif temp > heat_thresholds["high"]["temperature"]:
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
            # Check for frequent 100-year flood events using NOAA data
            frequent_100_year_floods = await self._check_frequent_100_year_floods(historical_data)
            if frequent_100_year_floods:
                risks.append({
                    "type": "Flooding",
                    "severity": "Super Extreme",
                    "description": "Frequent 100-year flood events detected in the past five years",
                    "sources": flood_thresholds["high"]["sources"],
                    "recommendations": [
                        "Immediate evacuation may be necessary",
                        "Contact local emergency services",
                        "Review and update flood preparedness plans",
                        "Consider long-term flood mitigation strategies"
                    ]
                })
            elif rain_1h > flood_thresholds["high"]["rainfall_1h"]:
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
                        "Be cautious with outdoor activities",
                        "Monitor local fire conditions",
                        "Prepare for potential fire outbreaks"
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
                        "Follow emergency instructions"
                    ]
                })
            elif "storm" in main:
                risks.append({
                    "type": "Extreme Storms",
                    "severity": "Medium",
                    "description": "Storm conditions detected",
                    "sources": storm_thresholds["medium"]["sources"],
                    "recommendations": [
                        "Stay indoors if possible",
                        "Monitor local weather updates",
                        "Be prepared for power outages"
                    ]
                })
        
        return risks

    async def _get_historical_data(self, lat: float, lon: float) -> Dict:
        """Get historical weather data from NOAA."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 5)  # 5 years of data
        
        try:
            historical_data = await self.noaa_data.get_severe_weather_data(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                location=f"{lat},{lon}",
                data_type="all",
                format="json"
            )
            
            if historical_data["status"] == "error":
                logger.warning(f"Failed to fetch historical data: {historical_data.get('error')}")
                return {}
                
            return historical_data["result"]
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return {}

    async def _check_frequent_100_year_floods(self, historical_data: Dict) -> bool:
        """Check for frequent 100-year flood events in historical data."""
        if not historical_data:
            return False
            
        try:
            # Analyze flood events from historical data
            flood_events = [event for event in historical_data.get("events", [])
                          if event.get("type") == "flood"]
            
            # Count significant flood events
            significant_floods = sum(1 for event in flood_events
                                  if event.get("severity", 0) >= 0.8)  # 80% of 100-year flood
            
            return significant_floods >= 2  # Two or more significant floods in 5 years
            
        except Exception as e:
            logger.error(f"Error checking flood frequency: {str(e)}")
            return False

    async def _check_frequent_extreme_heat(self, historical_data: Dict) -> bool:
        """Check for frequent extreme heat events in historical data."""
        if not historical_data:
            return False
            
        try:
            # Analyze heat events from historical data
            heat_events = [event for event in historical_data.get("events", [])
                         if event.get("type") == "heat"]
            
            # Count extreme heat events
            extreme_heat = sum(1 for event in heat_events
                             if event.get("severity", 0) >= 0.9)  # 90th percentile
            
            return extreme_heat >= 3  # Three or more extreme heat events in 5 years
            
        except Exception as e:
            logger.error(f"Error checking heat frequency: {str(e)}")
            return False

async def main():
    """Example usage of the ClimateRiskAnalyzer."""
    # Initialize analyzer with both API keys
    analyzer = ClimateRiskAnalyzer(
        openweather_api_key="your_openweather_api_key",
        noaa_api_key="your_noaa_api_key"
    )
    
    # Example coordinates (New York City)
    lat, lon = 40.7128, -74.0060
    
    try:
        # Analyze risks
        risks = await analyzer.analyze_risks(lat, lon)
        
        # Print results
        print("\nClimate Risk Analysis Results:")
        print("=============================")
        for risk in risks:
            print(f"\nRisk Type: {risk['type']}")
            print(f"Severity: {risk['severity']}")
            print(f"Description: {risk['description']}")
            print("\nRecommendations:")
            for rec in risk['recommendations']:
                print(f"- {rec}")
            print("\nSources:")
            for source in risk['sources']:
                print(f"- {source}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 