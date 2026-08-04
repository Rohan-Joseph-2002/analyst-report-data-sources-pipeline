"""
AUTHOR: Rohan Joseph
PURPOSE: Summarize the extraction output into source-frequency, contributor-frequency, and
         top-level metric tables written to analysis-output.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import io, settings, validation
from src.logger import capture_script_console_to_markdown
from src.utils import print_section_header, print_stage_banner, print_status



# ============================================================
# Settings
# ============================================================

LONG_INPUT_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d002_regex_source_extraction_long.csv"
)
SOURCE_FREQUENCY_PATH = os.path.join(settings.ANALYSIS_OUTPUT_DIR, "a001_source_frequency.csv")
CONTRIBUTOR_FREQUENCY_PATH = os.path.join(
    settings.ANALYSIS_OUTPUT_DIR, "a001_contributor_source_frequency.csv"
)
SUMMARY_METRICS_PATH = os.path.join(settings.ANALYSIS_OUTPUT_DIR, "a001_summary_metrics.csv")



# ============================================================
# Functions
# ============================================================

def build_source_frequency(regex_long_df):
    """
    Count how many times each source appears across the long extraction output.
    This surfaces which data sources analysts cite most often.
    """

    if regex_long_df.empty:
        return pd.DataFrame(columns = ["Source Name", "Frequency"])

    frequency = (
        regex_long_df.groupby("Source Name", as_index = False)
        .size()
        .rename(columns = {"size": "Frequency"})
        .sort_values(by = ["Frequency", "Source Name"], ascending = [False, True])
        .reset_index(drop = True)
    )

    return frequency


def build_contributor_source_frequency(regex_long_df):
    """
    Count source citations per contributor across the long extraction output.
    This shows which contributors rely on which data sources most often.
    """

    if regex_long_df.empty:
        return pd.DataFrame(columns = ["Contributor", "Source Name", "Frequency"])

    frequency = (
        regex_long_df.groupby(["Contributor", "Source Name"], as_index = False)
        .size()
        .rename(columns = {"size": "Frequency"})
        .sort_values(
            by = ["Frequency", "Contributor", "Source Name"], ascending = [False, True, True]
        )
        .reset_index(drop = True)
    )

    return frequency


def build_summary_metrics(regex_long_df):
    """
    Build compact top-level metrics describing the extraction output.
    This gives a quick, reviewable snapshot after the pipeline finishes.
    """

    has_rows = not regex_long_df.empty
    unique_sources = int(regex_long_df["Source Name"].nunique()) if has_rows else 0
    unique_documents = int(regex_long_df["DocumentID"].nunique()) if has_rows else 0
    unique_contributors = int(regex_long_df["Contributor"].nunique()) if has_rows else 0

    metrics = [
        {"section": "regex_stage", "metric": "row_count", "value": len(regex_long_df)},
        {"section": "regex_stage", "metric": "unique_sources", "value": unique_sources},
        {"section": "regex_stage", "metric": "matched_documents", "value": unique_documents},
        {"section": "regex_stage", "metric": "matched_contributors", "value": unique_contributors},
    ]

    return pd.DataFrame(metrics)



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Read the long extraction table and write source, contributor, and metric summaries.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Extraction Output")

    validation.require_existing_file(LONG_INPUT_PATH, context = "regex long output")
    regex_long_df = io.read_csv(LONG_INPUT_PATH, keep_empty_as_str = True)

    print_status(f"Loaded {len(regex_long_df)} long-output rows.")

    print_section_header("Summarizing Source Frequencies")

    source_frequency_df = build_source_frequency(regex_long_df)
    contributor_frequency_df = build_contributor_source_frequency(regex_long_df)
    summary_metrics_df = build_summary_metrics(regex_long_df)

    io.write_csv(source_frequency_df, SOURCE_FREQUENCY_PATH)
    io.write_csv(contributor_frequency_df, CONTRIBUTOR_FREQUENCY_PATH)
    io.write_csv(summary_metrics_df, SUMMARY_METRICS_PATH)

    print_status(f"Wrote 3 summary tables ({len(source_frequency_df)} unique sources).")


def main():
    """
    Run the frequency-analysis stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Analysis 001 | Source Frequency Analysis")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "a001_source_frequency_analysis",
        log_dir = settings.LOG_DIR,
    )
