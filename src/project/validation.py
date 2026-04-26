"""
AUTHOR: Rohan Joseph
PURPOSE: Validation helpers for schema and runtime checks.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os

import pandas as pd



"""
Functions
"""

def require_columns(df: pd.DataFrame, required_columns: list[str], context: str) -> None:
    """
    Validate that a DataFrame contains the expected columns.
    This helps fail early and clearly when upstream raw data schemas change.
    """

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns in {context}: {missing_columns}")


def require_existing_file(file_path: str, label: str) -> None:
    """
    Validate that a required file exists on disk.
    This helps environment checks before stage execution begins.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing required {label}: {file_path}")
