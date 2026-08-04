"""
AUTHOR: Rohan Joseph
PURPOSE: Provide fail-fast checks for required columns and files so that stages stop with
         a clear message instead of a confusing error deep in the pipeline.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os



# ============================================================
# Exceptions
# ============================================================

class ValidationError(Exception):
    """
    Raised when an input fails a precondition check.
    This is a custom exception to distinguish validation failures from other errors.
    """



# ============================================================
# Functions
# ============================================================

def require_columns(df, columns, context = "dataframe"):
    """
    Check that the DataFrame contains every required column and raise if any are missing.
    This fails fast with a clear message instead of a confusing error deep inside a stage.
    """

    missing = [column for column in columns if column not in df.columns]
    
    if missing:
        raise ValidationError(
            f"{context} is missing required columns: {missing}. Present: {list(df.columns)}"
        )


def require_existing_file(path, context = "input file"):
    """
    Check that the given file exists and raise if it does not.
    This turns a bare FileNotFoundError into an actionable, human-readable message.
    """

    if not os.path.isfile(path):
        raise ValidationError(
            f"{context} not found: {path}. In sample mode, check the committed samples in input/."
        )

    return path
