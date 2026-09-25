"""
Data Loader module for Brazilian E-Commerce Analytics.
Handles loading raw datasets from CSV files with appropriate dtypes and encoding.
"""
import os
import pandas as pd
from typing import Dict, Optional
from src.config import RAW_DATA_DIR, FILES, DATE_COLUMNS


def load_raw_dataset(name: str, nrows: Optional[int] = None) -> pd.DataFrame:
    """
    Load a single raw dataset by key name.

    Parameters:
    -----------
    name : str
        Key from config.FILES (e.g. 'orders', 'customers', etc.)
    nrows : int, optional
        Number of rows to read (useful for quick sampling)

    Returns:
    --------
    pd.DataFrame
    """
    if name not in FILES:
        raise ValueError(f"Unknown dataset name: {name}. Available: {list(FILES.keys())}")

    file_path = RAW_DATA_DIR / FILES[name]
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")

    # Check date columns to parse
    parse_dates = DATE_COLUMNS.get(name, False)

    # Handle utf-8-sig for BOM in category translation
    encoding = "utf-8-sig" if name == "category_translation" else "utf-8"

    df = pd.read_csv(
        file_path,
        parse_dates=parse_dates,
        nrows=nrows,
        encoding=encoding
    )

    # Clean any whitespace or BOM from column names
    df.columns = [col.strip().replace('﻿', '') for col in df.columns]

    return df


def load_all_raw_datasets(nrows: Optional[int] = None) -> Dict[str, pd.DataFrame]:
    """
    Load all 9 datasets into a dictionary of DataFrames.

    Parameters:
    -----------
    nrows : int, optional
        Number of rows to read per dataset.

    Returns:
    --------
    Dict[str, pd.DataFrame]
    """
    datasets = {}
    for key in FILES.keys():
        datasets[key] = load_raw_dataset(key, nrows=nrows)
    return datasets


if __name__ == "__main__":
    print("Testing data loader...")
    data = load_all_raw_datasets(nrows=100)
    for name, df in data.items():
        print(f"Loaded '{name}': {df.shape[0]} rows, {df.shape[1]} columns")
