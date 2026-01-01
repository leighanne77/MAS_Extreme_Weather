"""
Pollinator Data Scraper/Loader
Source: https://www.fs.usda.gov/wildflowers/pollinators
Refresh: Quarterly (manual or scheduled job)
"""
import requests
import logging
from bs4 import BeautifulSoup

POLLINATOR_URL = "https://www.fs.usda.gov/wildflowers/pollinators"

# Example: Scrape pollinator info (species, status, etc.)
def scrape_pollinator_data() -> list:
    """
    Scrape pollinator data from USFS site.
    Returns:
        list: List of pollinator records (dicts)
    """
    try:
        resp = requests.get(POLLINATOR_URL, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Example: Find all pollinator species listed on the page
        pollinators = []
        for li in soup.find_all("li"):
            text = li.get_text(strip=True)
            if "bee" in text.lower() or "butterfly" in text.lower():
                pollinators.append({"name": text})
        return pollinators
    except Exception as e:
        logging.error(f"Pollinator scrape error: {e}", exc_info=True)
        return []
