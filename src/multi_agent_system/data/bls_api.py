"""
BLS (Bureau of Labor Statistics) Public Data API Integration
Docs: https://www.bls.gov/developers/
"""
import os
import requests
import logging

BLS_API_KEY = os.getenv("BLS_API_KEY")
BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

def get_bls_data(series_ids: list, start_year: str, end_year: str) -> dict:
    """
    Fetch data from BLS Public Data API.
    Args:
        series_ids (list): List of BLS series IDs
        start_year (str): Start year
        end_year (str): End year
    Returns:
        dict: API response
    """
    headers = {"Content-type": "application/json"}
    data = {
        "seriesid": series_ids,
        "startyear": start_year,
        "endyear": end_year,
        "registrationkey": BLS_API_KEY
    }
    try:
        resp = requests.post(BASE_URL, json=data, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"BLS API error: {e}", exc_info=True)
        return {}
