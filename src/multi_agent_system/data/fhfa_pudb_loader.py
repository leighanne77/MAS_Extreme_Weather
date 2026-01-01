"""
FHFA Public Use Database (PUDB) Loader
Docs: https://www.fhfa.gov/data/pudb

This module loads and filters FHFA PUDB datasets (CSV, TXT, Excel) for property, loan, and home price data.
Mark as [Ref] in documentation (not a live API).
"""
import pandas as pd
import os

def load_pudb_data(filepath: str) -> pd.DataFrame:
    """
    Load FHFA PUDB data from CSV, TXT, or Excel file.
    Args:
        filepath (str): Path to PUDB data file
    Returns:
        pd.DataFrame: Loaded data
    """
    ext = os.path.splitext(filepath)[-1].lower()
    if ext in [".csv", ".txt"]:
        return pd.read_csv(filepath)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def filter_pudb_data(df: pd.DataFrame, **filters) -> pd.DataFrame:
    """
    Filter PUDB DataFrame by column values.
    Args:
        df (pd.DataFrame): PUDB data
        filters: Column=value pairs to filter
    Returns:
        pd.DataFrame: Filtered data
    """
    for col, val in filters.items():
        df = df[df[col] == val]
    return df
