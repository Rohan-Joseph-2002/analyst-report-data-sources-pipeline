"""
AUTHOR: Rohan Joseph
PURPOSE: Test the Stage 1 preparation helpers that clean reports and reshape the source
         dictionary, plus the schema validation guard.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys
import pytest
import subprocess
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import settings, validation
from src.logger import capture_script_console_to_markdown
from data.d001_prepare_input_data import (
    prepare_reports_dataframe,
    reshape_alternative_sources,
)



# ============================================================
# Tests
# ============================================================

def test_prepare_reports_dataframe_adds_cleaned_columns():
    """
    Check that report preparation adds the cleaned-text, preview, and word-count columns.
    This locks the Stage 1 report schema that the extraction stage depends on.
    """

    raw = pd.DataFrame(
        [
            {
                "DocumentID": "DOC1", "Date": "2024-01-01", "Year": 2024,
                "Contributor": "Alpha", "Report File Ticker": "X.N", "Partial Title": "Title",
                "Pages": 3, "PDF File Name": "x.pdf",
                "Report Text": "According to  Demo   Analytics, results improved.",
            }
        ]
    )

    prepared = prepare_reports_dataframe(raw)
    cleaned = prepared.loc[0, "Report Text Cleaned"]

    assert cleaned == "According to Demo Analytics, results improved."
    assert prepared.loc[0, "Report Word Count"] == 6


def test_reshape_alternative_sources_produces_long_lookup():
    """
    Check that the wide source dictionary reshapes into the long, de-duplicated lookup.
    This ensures downstream matching receives normalized source rows.
    """

    raw = pd.DataFrame(
        {
            "List of Alternative Company Names | ATT = 1": ["Demo Analytics", "Sample Data Co"],
            "List of Alternative Product Names | ATT = 1": ["Example Insights", None],
        }
    )

    prepared = reshape_alternative_sources(raw)

    assert len(prepared) == 3
    assert "Demo Analytics" in prepared["source_name"].tolist()
    assert "Example Insights" in prepared["source_name"].tolist()


def test_require_columns_raises_on_missing():
    """
    Check that require_columns raises when a required column is absent.
    This ensures Stage 1 fails fast on a malformed report input.
    """

    frame = pd.DataFrame({"DocumentID": ["DOC1"]})

    with pytest.raises(validation.ValidationError):
        validation.require_columns(frame, ["DocumentID", "Report Text"])



# ============================================================
# Main Execution
# ============================================================

def main():
    """
    Run this test module through pytest in a subprocess and echo its output.
    This logs the test run like a pipeline script without the tee fighting pytest's capture.
    """

    command = [sys.executable, "-m", "pytest", __file__, "-v"]
    result = subprocess.run(command, capture_output = True, text = True)

    print(result.stdout, end = "")
    print(result.stderr, end = "")


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "t001_prepare_input_data",
        log_dir = settings.LOG_DIR,
    )
