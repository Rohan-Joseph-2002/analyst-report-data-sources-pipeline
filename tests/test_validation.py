"""
AUTHOR: Rohan Joseph
PURPOSE: Unit tests for validation helpers.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import pandas as pd
import pytest


# --- Import project-specific utilities and pipeline code ---
from project.validation import require_columns



"""
Tests
"""

def test_require_columns_raises_on_missing_columns() -> None:
    """
    Validate that missing required columns raise a clear error.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    sample_df = pd.DataFrame({"DocumentID": [1]})

    with pytest.raises(ValueError):
        require_columns(sample_df, ["DocumentID", "Report Text"], "sample frame")
