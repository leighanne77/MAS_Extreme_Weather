"""
EPA STORET Data Warehouse API Integration (via Water Quality Portal)
Docs: https://www.waterqualitydata.us/webservices_documentation/
"""
import requests
import logging

BASE_URL = "https://www.waterqualitydata.us/"

def get_storet_data(endpoint: str, params: dict = None) -> dict:
    """
    Fetch data from EPA STORET/Water Quality Portal API.
    Args:
        endpoint (str): API endpoint (e.g., 'Station/search')
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
        logging.error(f"EPA STORET API error: {e}", exc_info=True)
        return {}
