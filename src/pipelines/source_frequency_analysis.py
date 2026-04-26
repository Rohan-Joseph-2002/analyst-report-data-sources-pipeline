"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 3 pipeline for regex source-frequency summaries.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-26
MODIFIED BY: OpenAI Codex
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from analysis.frequency_analysis import (
    build_contributor_source_frequency,
    build_source_frequency,
    build_summary_metrics,
)
from project.utils import (
    ensure_parent_dir,
    print_section_header,
    print_stage_banner,
    print_status,
)



"""
Functions
"""

def run_source_frequency_analysis(config, paths) -> None:
    """
    Execute Stage 3 for the analyst report data sources pipeline.
    This keeps execution flow centralized instead of spreading stage orchestration across multiple callers.
    """

    print_stage_banner("Stage 3 | Source Frequency Analysis")
    print_section_header("Loading Regex Outputs")

    regex_long_path = os.path.join(paths.stage_002_dir, "regex_source_extraction_long.csv")

    regex_long_df = pd.read_csv(regex_long_path, low_memory = False)

    print_status(f"Loaded {len(regex_long_df):,} regex long-output rows.")

    print_section_header("Summarizing Source Frequencies")

    regex_frequency_input_df = regex_long_df.copy()
    regex_frequency_input_df["Source Count"] = 1

    regex_frequency_df = build_source_frequency(
        source_df = regex_frequency_input_df,
        source_column = "Source Name",
        count_column = "Source Count",
    )
    contributor_frequency_df = build_contributor_source_frequency(regex_long_df = regex_long_df)
    summary_metrics_df = build_summary_metrics(regex_long_df = regex_long_df)

    regex_frequency_path = os.path.join(paths.stage_003_dir, "regex_source_frequency.csv")
    contributor_frequency_path = os.path.join(paths.stage_003_dir, "contributor_source_frequency.csv")
    summary_metrics_path = os.path.join(paths.stage_003_dir, "source_frequency_summary_metrics.csv")

    for output_path, output_df in [
        (regex_frequency_path, regex_frequency_df),
        (contributor_frequency_path, contributor_frequency_df),
        (summary_metrics_path, summary_metrics_df),
    ]:
        ensure_parent_dir(output_path)
        output_df.to_csv(output_path, index = False)

    print_status(f"Regex frequency shape: {regex_frequency_df.shape}.")
    print_status(f"Contributor frequency shape: {contributor_frequency_df.shape}.")
    print_status(f"Summary metrics shape: {summary_metrics_df.shape}.")
    print_status(f"Exported stage output: {os.path.basename(regex_frequency_path)}.")
    print_status(f"Exported stage output: {os.path.basename(contributor_frequency_path)}.")
    print_status(f"Exported stage output: {os.path.basename(summary_metrics_path)}.")
