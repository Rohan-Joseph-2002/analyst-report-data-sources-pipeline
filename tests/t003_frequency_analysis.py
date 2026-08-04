"""
AUTHOR: Rohan Joseph
PURPOSE: Test the analysis-stage helpers that build source-frequency and summary-metric
         tables from the long extraction output.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys
import subprocess
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import settings
from src.logger import capture_script_console_to_markdown
from analysis.a001_source_frequency_analysis import build_source_frequency, build_summary_metrics



# ============================================================
# Tests
# ============================================================

def test_build_source_frequency_counts_sources():
    """
    Check that source frequency counts occurrences and ranks the most common first.
    This locks the headline source-frequency table behavior.
    """

    long_df = pd.DataFrame(
        [
            {"Contributor": "Alpha", "Source Name": "Demo Analytics", "DocumentID": "D1"},
            {"Contributor": "Beta", "Source Name": "Demo Analytics", "DocumentID": "D2"},
            {"Contributor": "Alpha", "Source Name": "Sample Data Co", "DocumentID": "D1"},
        ]
    )

    frequency = build_source_frequency(long_df)

    assert frequency.loc[0, "Source Name"] == "Demo Analytics"
    assert frequency.loc[0, "Frequency"] == 2


def test_build_summary_metrics_reports_counts():
    """
    Check that summary metrics report the row count and unique-source count.
    This locks the top-level review snapshot produced after the pipeline runs.
    """

    long_df = pd.DataFrame(
        [
            {"Contributor": "Alpha", "Source Name": "Demo Analytics", "DocumentID": "D1"},
            {"Contributor": "Beta", "Source Name": "Sample Data Co", "DocumentID": "D2"},
        ]
    )

    metrics = build_summary_metrics(long_df)
    row_count = metrics.loc[metrics["metric"] == "row_count", "value"].iloc[0]
    unique_sources = metrics.loc[metrics["metric"] == "unique_sources", "value"].iloc[0]

    assert row_count == 2
    assert unique_sources == 2



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
        script_name = "t003_frequency_analysis",
        log_dir = settings.LOG_DIR,
    )
