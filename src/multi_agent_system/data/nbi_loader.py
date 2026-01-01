"""
National Bridge Inventory (NBI) Data Loader
Docs: https://www.fhwa.dot.gov/bridge/nbi/ascii.cfm
"""
import pandas as pd
import os

NBI_DATA_PATH = os.getenv("NBI_DATA_PATH", "data/curated/nbi/NBI2024.txt")


def load_nbi_data(filepath: str = None) -> pd.DataFrame:
    """
    Load NBI data from a fixed-width ASCII file or CSV.
    Args:
        filepath (str): Path to NBI data file
    Returns:
        pd.DataFrame: NBI data
    """
    path = filepath or NBI_DATA_PATH
    # Adjust colspecs and names as needed for the NBI format
    return pd.read_fwf(path)
