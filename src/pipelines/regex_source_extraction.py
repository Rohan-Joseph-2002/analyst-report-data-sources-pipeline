"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 2 pipeline for rule-based source extraction from analyst reports.
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


# --- Import project-specific utilities and pipeline code ---
from extraction.regex_sources import (
    extract_potential_source_phrases,
    find_explicit_dictionary_mentions,
    match_dictionary_sources,
    split_source_candidates,
    summarize_matched_sources,
)
from project.settings import REGEX_LONG_COLUMNS, REGEX_SUMMARY_COLUMNS
from project.utils import (
    ensure_parent_dir,
    print_section_header,
    print_stage_banner,
    print_status,
    stringify_list,
)



"""
Functions
"""

def build_regex_stage_outputs(prepared_reports_df: pd.DataFrame, prepared_sources_df: pd.DataFrame, similarity_threshold: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build the Stage 2 summary and long-form outputs.
    This helps keep the core extraction logic testable outside the script entrypoint.
    """

    summary_rows: list[dict] = []
    long_rows: list[dict] = []

    for _, row in prepared_reports_df.iterrows():
        row_dict = row.to_dict()
        potential_phrases = extract_potential_source_phrases(report_text = row_dict["Report Text"])
        candidate_sources = split_source_candidates(potential_phrases = potential_phrases)
        explicit_mentions = find_explicit_dictionary_mentions(
            report_text = row_dict["Report Text Cleaned"],
            source_lookup_df = prepared_sources_df,
        )
        matched_sources = match_dictionary_sources(
            candidate_sources = candidate_sources,
            source_lookup_df = prepared_sources_df,
            similarity_threshold = similarity_threshold,
        )

        summary_rows.append(
            {
                "DocumentID": row_dict["DocumentID"],
                "Year": row_dict["Year"],
                "Date": row_dict["Date"],
                "Contributor": row_dict["Contributor"],
                "Report File Ticker": row_dict["Report File Ticker"],
                "Partial Title": row_dict["Partial Title"],
                "Pages": row_dict["Pages"],
                "PDF File Name": row_dict["PDF File Name"],
                "Potential Source Phrases": stringify_list(potential_phrases),
                "Regex Candidate Sources": stringify_list(candidate_sources),
                "Explicit Mentioned Sources": stringify_list(summarize_matched_sources(explicit_mentions)),
                "Matched Alternative Sources": stringify_list(summarize_matched_sources(matched_sources)),
                "Matched Source Count": len({source["Source Name Normalized"] for source in matched_sources + explicit_mentions}),
            }
        )

        for matched_source in explicit_mentions + matched_sources:
            long_rows.append(
                {
                    "DocumentID": row_dict["DocumentID"],
                    "Year": row_dict["Year"],
                    "Date": row_dict["Date"],
                    "Contributor": row_dict["Contributor"],
                    "Report File Ticker": row_dict["Report File Ticker"],
                    "PDF File Name": row_dict["PDF File Name"],
                    "Source Name": matched_source["Source Name"],
                    "Source Name Normalized": matched_source["Source Name Normalized"],
                    "Source Origin": matched_source["Source Origin"],
                    "Source Group": matched_source["Source Group"],
                    "Attention Tier": matched_source["Attention Tier"],
                    "Match Score": matched_source["Match Score"],
                }
            )

    summary_df = pd.DataFrame(summary_rows, columns = REGEX_SUMMARY_COLUMNS)
    long_df = pd.DataFrame(long_rows, columns = REGEX_LONG_COLUMNS).drop_duplicates().reset_index(drop = True)

    return summary_df, long_df


def run_regex_source_extraction(config, paths) -> None:
    """
    Execute Stage 2 for the analyst report data sources pipeline.
    This keeps execution flow centralized instead of spreading stage orchestration across multiple callers.
    """

    print_stage_banner("Stage 2 | Regex Source Extraction")
    print_section_header("Loading Prepared Inputs")

    prepared_reports_path = os.path.join(paths.stage_001_dir, "prepared_reports.csv")
    prepared_sources_path = os.path.join(paths.stage_001_dir, "prepared_alternative_sources.csv")

    prepared_reports_df = pd.read_csv(prepared_reports_path, low_memory = False)
    prepared_sources_df = pd.read_csv(prepared_sources_path, low_memory = False)

    print_status(f"Loaded {len(prepared_reports_df):,} prepared reports.")
    print_status(f"Loaded {len(prepared_sources_df):,} prepared source reference rows.")

    print_section_header("Extracting Sources")

    summary_df, long_df = build_regex_stage_outputs(
        prepared_reports_df = prepared_reports_df,
        prepared_sources_df = prepared_sources_df,
        similarity_threshold = config.regex_similarity_threshold,
    )

    summary_output_path = os.path.join(paths.stage_002_dir, "regex_source_extraction_summary.csv")
    long_output_path = os.path.join(paths.stage_002_dir, "regex_source_extraction_long.csv")

    ensure_parent_dir(summary_output_path)
    summary_df.to_csv(summary_output_path, index = False)
    long_df.to_csv(long_output_path, index = False)

    print_status(f"Regex summary shape: {summary_df.shape}.")
    print_status(f"Regex long output shape: {long_df.shape}.")
    print_status(f"Exported stage output: {os.path.basename(summary_output_path)}.")
    print_status(f"Exported stage output: {os.path.basename(long_output_path)}.")
