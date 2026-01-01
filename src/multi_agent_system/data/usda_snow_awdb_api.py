"""
USDA NRCS Snow AWDB REST API Integration
Docs: https://wcc.sc.egov.usda.gov/awdbRestApi/swagger-ui/index.html
"""
import requests
import logging

BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/"

def get_awdb_data(endpoint: str, params: dict = None) -> dict:
    """
    Fetch data from USDA NRCS AWDB REST API.
    Args:
        endpoint (str): API endpoint (e.g., 'data/getData')
        params (dict): Query parameters
    Returns:
        dict: API response
    """
    url = BASE_URL + endpoint
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"AWDB API error: {e}", exc_info=True)
        return {}
