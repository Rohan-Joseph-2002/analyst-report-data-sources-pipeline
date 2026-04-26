"""
AUTHOR: Rohan Joseph
PURPOSE: Input and output helpers for stage scripts.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""

"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import pandas as pd



"""
Functions
"""

def read_reports_dataframe(file_path: str, max_reports: int | None = None) -> pd.DataFrame:
    """
    Read the cleaned analyst-report sample file.
    This helps centralize CSV loading and optional row-limiting.
    """

    reports_df = pd.read_csv(file_path, low_memory = False)

    if max_reports is not None:
        reports_df = reports_df.head(max_reports).copy()

    return reports_df


def read_alternative_sources_dataframe(file_path: str) -> pd.DataFrame:
    """
    Read the local alternative-source dictionary sample.
    This helps centralize reference-data loading.
    """

    return pd.read_csv(file_path, low_memory = False)
