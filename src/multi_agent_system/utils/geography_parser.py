"""
Geography Parser Utility

Parses location strings and identifies administrative hierarchy for US and India.
Supports hierarchical geography parsing for government data access.

Compliance:
- Uses "extreme weather" terminology (not "climate")
- Decision support tool only - results are for user review
- Supports hierarchical geography as per project rules
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class GeographicContext:
    """Represents parsed geographic location with administrative hierarchy."""
    location: str
    country: Optional[str] = None
    region: Optional[str] = None
    state_province: Optional[str] = None
    district_county: Optional[str] = None  # District (India) or County (US)
    block_city: Optional[str] = None  # Block (India) or City/Town (US)
    village_neighborhood: Optional[str] = None  # Village (India) or Neighborhood (US)
    administrative_level: Optional[str] = None  # Identified level: country, state, district/county, block/city, village/neighborhood
    bioregion: Optional[str] = None
    location_type: Optional[str] = None  # coastal, riverine, urban, rural, agricultural


class GeographyParser:
    """Parser for location strings with support for US and India administrative hierarchies."""
    
    # US States
    US_STATES = {
        "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
        "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
        "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
        "maine", "maryland", "massachusetts", "michigan", "minnesota",
        "mississippi", "missouri", "montana", "nebraska", "nevada",
        "new hampshire", "new jersey", "new mexico", "new york",
        "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
        "pennsylvania", "rhode island", "south carolina", "south dakota",
        "tennessee", "texas", "utah", "vermont", "virginia", "washington",
        "west virginia", "wisconsin", "wyoming", "district of columbia"
    }
    
    # India States and Union Territories
    INDIA_STATES = {
        "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
        "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand",
        "karnataka", "kerala", "madhya pradesh", "maharashtra", "manipur",
        "meghalaya", "mizoram", "nagaland", "odisha", "punjab", "rajasthan",
        "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh",
        "uttarakhand", "west bengal", "andaman and nicobar islands",
        "chandigarh", "dadra and nagar haveli and daman and diu", "delhi",
        "jammu and kashmir", "ladakh", "lakshadweep", "puducherry"
    }
    
    # Common location type indicators
    LOCATION_TYPE_INDICATORS = {
        "coastal": ["bay", "coast", "beach", "shore", "ocean", "sea", "gulf", "lagoon", "estuary"],
        "riverine": ["river", "creek", "stream", "watershed", "floodplain", "delta"],
        "urban": ["city", "town", "municipality", "metro", "urban"],
        "rural": ["rural", "countryside", "village", "hamlet"],
        "agricultural": ["farm", "agricultural", "cropland", "pasture"]
    }
    
    def __init__(self):
        """Initialize the geography parser."""
        self.administrative_hierarchies = self._initialize_hierarchies()
    
    def _initialize_hierarchies(self) -> dict[str, dict[str, Any]]:
        """Initialize administrative hierarchies for supported countries."""
        return {
            "us": {
                "levels": ["country", "state", "county", "city", "neighborhood"],
                "level_names": {
                    "country": "United States",
                    "state": "State",
                    "county": "County",
                    "city": "City/Town",
                    "neighborhood": "Neighborhood"
                },
                "country_code": "US"
            },
            "india": {
                "levels": ["country", "state", "district", "block", "village"],
                "level_names": {
                    "country": "India",
                    "state": "State/Union Territory",
                    "district": "District",
                    "block": "Block",
                    "village": "Village"
                },
                "country_code": "IN"
            }
        }
    
    def parse_location(self, location: str) -> GeographicContext:
        """
        Parse a location string and identify administrative hierarchy.
        
        Args:
            location: Location string (e.g., "Mobile Bay, Alabama", "Chennai, Tamil Nadu, India")
        
        Returns:
            GeographicContext with parsed location information
        """
        if not location or not location.strip():
            return GeographicContext(location=location)
        
        location_lower = location.lower().strip()
        context = GeographicContext(location=location)
        
        # Identify country
        country = self._identify_country(location_lower)
        context.country = country
        
        if not country:
            logger.warning(f"Could not identify country for location: {location}")
            return context
        
        # Parse based on country
        if country == "us":
            self._parse_us_location(location, location_lower, context)
        elif country == "india":
            self._parse_india_location(location, location_lower, context)
        
        # Identify location type
        context.location_type = self._identify_location_type(location_lower)
        
        # Identify administrative level
        context.administrative_level = self._identify_administrative_level(context)
        
        return context
    
    def _identify_country(self, location_lower: str) -> Optional[str]:
        """Identify country from location string."""
        # Check for explicit country mentions
        if "india" in location_lower or "indian" in location_lower:
            return "india"
        if "usa" in location_lower or "united states" in location_lower or "u.s." in location_lower:
            return "us"
        
        # Check for US states
        for state in self.US_STATES:
            if state in location_lower:
                return "us"
        
        # Check for India states
        for state in self.INDIA_STATES:
            if state in location_lower:
                return "india"
        
        # Default to US if no clear indicator (for now)
        # This could be enhanced with geocoding in the future
        return None
    
    def _parse_us_location(self, location: str, location_lower: str, context: GeographicContext) -> None:
        """Parse US location string."""
        context.country = "us"
        
        # Common US location patterns:
        # "City, State"
        # "City, County, State"
        # "Neighborhood, City, State"
        # "State"
        # "County, State"
        
        # Try to extract state
        for state in self.US_STATES:
            if state in location_lower:
                context.state_province = self._normalize_state_name(state)
                break
        
        # Try to identify city/county patterns
        # Look for comma-separated patterns
        parts = [p.strip() for p in location.split(",")]
        
        if len(parts) >= 2:
            # Assume last part is state if it matches a state
            last_part = parts[-1].lower().strip()
            if last_part in self.US_STATES:
                context.state_province = self._normalize_state_name(last_part)
                
                # Second to last might be county or city
                if len(parts) >= 3:
                    context.district_county = parts[-2].strip()  # County
                    context.block_city = parts[-3].strip()  # City
                elif len(parts) >= 2:
                    context.block_city = parts[-2].strip()  # City
            else:
                # Last part might be city, second to last might be county
                if len(parts) >= 3:
                    context.district_county = parts[-2].strip()
                    context.block_city = parts[-1].strip()
                else:
                    context.block_city = parts[-1].strip()
        else:
            # Single part - might be just state or city
            if location_lower in self.US_STATES:
                context.state_province = self._normalize_state_name(location_lower)
            else:
                context.block_city = parts[0].strip()
    
    def _parse_india_location(self, location: str, location_lower: str, context: GeographicContext) -> None:
        """Parse India location string."""
        context.country = "india"
        
        # Common India location patterns:
        # "City, State"
        # "City, District, State"
        # "Village, Block, District, State"
        # "State"
        # "District, State"
        
        # Try to extract state
        for state in self.INDIA_STATES:
            if state in location_lower:
                context.state_province = self._normalize_state_name(state)
                break
        
        # Try to identify district/block/village patterns
        # Look for comma-separated patterns
        parts = [p.strip() for p in location.split(",")]
        
        if len(parts) >= 2:
            # Assume last part is state if it matches a state
            last_part = parts[-1].lower().strip()
            if last_part in self.INDIA_STATES:
                context.state_province = self._normalize_state_name(last_part)
                
                # Parse remaining parts (could be district, block, village, city)
                if len(parts) >= 4:
                    # Village, Block, District, State
                    context.village_neighborhood = parts[-4].strip()
                    context.block_city = parts[-3].strip()  # Block
                    context.district_county = parts[-2].strip()  # District
                elif len(parts) >= 3:
                    # Block, District, State or City, District, State
                    context.block_city = parts[-2].strip()  # Block or City
                    context.district_county = parts[-3].strip()  # District
                elif len(parts) >= 2:
                    # City, State or District, State
                    context.district_county = parts[-2].strip()  # District or City
            else:
                # Last part might be city, second to last might be district
                if len(parts) >= 3:
                    context.district_county = parts[-2].strip()
                    context.block_city = parts[-1].strip()
                else:
                    context.block_city = parts[-1].strip()
        else:
            # Single part - might be just state or city
            if location_lower in self.INDIA_STATES:
                context.state_province = self._normalize_state_name(location_lower)
            else:
                context.block_city = parts[0].strip()
    
    def _normalize_state_name(self, state: str) -> str:
        """Normalize state name to proper case."""
        # Handle special cases
        special_cases = {
            "new york": "New York",
            "new hampshire": "New Hampshire",
            "new jersey": "New Jersey",
            "new mexico": "New Mexico",
            "north carolina": "North Carolina",
            "north dakota": "North Dakota",
            "south carolina": "South Carolina",
            "south dakota": "South Dakota",
            "west virginia": "West Virginia",
            "district of columbia": "District of Columbia",
            "tamil nadu": "Tamil Nadu",
            "andhra pradesh": "Andhra Pradesh",
            "arunachal pradesh": "Arunachal Pradesh",
            "himachal pradesh": "Himachal Pradesh",
            "madhya pradesh": "Madhya Pradesh",
            "uttar pradesh": "Uttar Pradesh",
            "west bengal": "West Bengal",
            "andaman and nicobar islands": "Andaman and Nicobar Islands",
            "dadra and nagar haveli and daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
            "jammu and kashmir": "Jammu and Kashmir"
        }
        
        state_lower = state.lower()
        if state_lower in special_cases:
            return special_cases[state_lower]
        
        # Default: title case
        return state.title()
    
    def _identify_location_type(self, location_lower: str) -> Optional[str]:
        """Identify location type from location string."""
        for location_type, indicators in self.LOCATION_TYPE_INDICATORS.items():
            for indicator in indicators:
                if indicator in location_lower:
                    return location_type
        return None
    
    def _identify_administrative_level(self, context: GeographicContext) -> Optional[str]:
        """Identify the administrative level of the parsed location."""
        if not context.country:
            return None
        
        # Check from most specific to least specific
        if context.village_neighborhood:
            return "village" if context.country == "india" else "neighborhood"
        if context.block_city:
            return "block" if context.country == "india" else "city"
        if context.district_county:
            return "district" if context.country == "india" else "county"
        if context.state_province:
            return "state"
        if context.country:
            return "country"
        
        return None
    
    def get_administrative_hierarchy(self, country: str) -> dict[str, Any]:
        """
        Get administrative hierarchy structure for a country.
        
        Args:
            country: Country code ("us" or "india")
        
        Returns:
            Dict containing hierarchy structure
        """
        country_lower = country.lower()
        if country_lower in ["us", "usa", "united states"]:
            country_lower = "us"
        elif country_lower in ["india", "in"]:
            country_lower = "india"
        
        return self.administrative_hierarchies.get(country_lower, {})
    
    def identify_administrative_level(self, location: str, country: Optional[str] = None) -> Optional[str]:
        """
        Identify the administrative level of a location string.
        
        Args:
            location: Location string to analyze
            country: Optional country code to use (if not provided, will be detected)
        
        Returns:
            Administrative level string (country, state, district/county, block/city, village/neighborhood)
        """
        context = self.parse_location(location)
        
        if country:
            context.country = country.lower() if country else None
        
        return context.administrative_level


# Convenience functions for direct use
def parse_location(location: str) -> GeographicContext:
    """
    Parse a location string and return GeographicContext.
    
    Args:
        location: Location string (e.g., "Mobile Bay, Alabama", "Chennai, Tamil Nadu, India")
    
    Returns:
        GeographicContext with parsed location information
    """
    parser = GeographyParser()
    return parser.parse_location(location)


def get_administrative_hierarchy(country: str) -> dict[str, Any]:
    """
    Get administrative hierarchy structure for a country.
    
    Args:
        country: Country code ("us" or "india")
    
    Returns:
        Dict containing hierarchy structure
    """
    parser = GeographyParser()
    return parser.get_administrative_hierarchy(country)


def identify_administrative_level(location: str, country: Optional[str] = None) -> Optional[str]:
    """
    Identify the administrative level of a location string.
    
    Args:
        location: Location string to analyze
        country: Optional country code to use (if not provided, will be detected)
    
    Returns:
        Administrative level string
    """
    parser = GeographyParser()
    return parser.identify_administrative_level(location, country)




