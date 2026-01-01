"""
EPA Water Quality Exchange (WQX) API Integration
Docs: https://www.epa.gov/waterdata/water-quality-data-wqx
"""
import requests
import logging

BASE_URL = "https://www.waterqualitydata.us/"

def get_wqx_data(endpoint: str, params: dict = None) -> dict:
    """
    Fetch data from EPA WQX/Water Quality Portal API.
    Args:
        endpoint (str): API endpoint (e.g., 'Result/search')
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
        logging.error(f"EPA WQX API error: {e}", exc_info=True)
        return {}
