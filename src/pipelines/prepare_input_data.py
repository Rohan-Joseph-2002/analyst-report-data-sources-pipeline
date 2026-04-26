"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 1 pipeline for preparing analyst report sample inputs and alternative source references.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""

from __future__ import annotations



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from project.io import (
    read_alternative_sources_dataframe,
    read_reports_dataframe,
)
from project.settings import (
    ALTERNATIVE_SOURCE_COLUMN_MAP,
    PREPARED_REPORT_COLUMNS,
    PREPARED_SOURCE_COLUMNS,
    REFERENCE_SOURCE_EXCLUSIONS,
    REPORT_REQUIRED_COLUMNS,
)
from project.utils import (
    ensure_parent_dir,
    normalize_source_name,
    normalize_whitespace,
    print_section_header,
    print_stage_banner,
    print_status,
    truncate_text,
)
from project.validation import require_columns



"""
Functions
"""

def prepare_reports_dataframe(raw_reports_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the raw report sample input.
    This helps produce a stable stage-one report table for downstream extraction.
    """

    report_columns = [column for column in raw_reports_df.columns if not str(column).startswith("Unnamed:")]
    prepared_reports_df = raw_reports_df[report_columns].copy()

    require_columns(prepared_reports_df, REPORT_REQUIRED_COLUMNS, "raw reports input")

    prepared_reports_df["Report Text"] = prepared_reports_df["Report Text"].fillna("").astype(str)
    prepared_reports_df["Report Text Cleaned"] = prepared_reports_df["Report Text"].map(normalize_whitespace)
    prepared_reports_df["Report Text Preview"] = prepared_reports_df["Report Text Cleaned"].map(truncate_text)
    prepared_reports_df["Report Word Count"] = prepared_reports_df["Report Text Cleaned"].map(lambda value: len(value.split()))

    return prepared_reports_df[PREPARED_REPORT_COLUMNS].copy()


def reshape_alternative_sources(raw_sources_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the wide alternative-source dictionary into a long prepared lookup table.
    This helps make explicit mentions and fuzzy matching easier downstream.
    """

    prepared_rows: list[dict] = []

    for column_name, column_metadata in ALTERNATIVE_SOURCE_COLUMN_MAP.items():
        if column_name not in raw_sources_df.columns:
            continue

        for raw_value in raw_sources_df[column_name].dropna().tolist():
            source_name = normalize_whitespace(str(raw_value))
            source_name_normalized = normalize_source_name(source_name)

            if not source_name or not source_name_normalized:
                continue

            if source_name_normalized.lower() in REFERENCE_SOURCE_EXCLUSIONS:
                continue

            prepared_rows.append(
                {
                    "source_name": source_name,
                    "source_name_normalized": source_name_normalized,
                    "source_group": column_metadata["source_group"],
                    "attention_tier": column_metadata["attention_tier"],
                }
            )

    prepared_sources_df = pd.DataFrame(prepared_rows).drop_duplicates().reset_index(drop = True)

    if prepared_sources_df.empty:
        return pd.DataFrame(columns = PREPARED_SOURCE_COLUMNS)

    attention_rank_map = {
        "ATT = 1": 0,
        "0 < ATT < 1": 1,
        "ATT = 0": 2,
    }
    source_group_rank_map = {
        "alternative_company_name": 0,
        "alternative_product_name": 1,
    }

    prepared_sources_df["attention_rank"] = prepared_sources_df["attention_tier"].map(attention_rank_map).fillna(9)
    prepared_sources_df["source_group_rank"] = prepared_sources_df["source_group"].map(source_group_rank_map).fillna(9)

    prepared_sources_df = (
        prepared_sources_df.sort_values(
            by = ["source_name_normalized", "attention_rank", "source_group_rank", "source_name"],
            ascending = [True, True, True, True],
        )
        .drop_duplicates(subset = ["source_name_normalized"], keep = "first")
        .reset_index(drop = True)
    )

    return prepared_sources_df[PREPARED_SOURCE_COLUMNS].copy()


def run_prepare_input_data(config, paths) -> None:
    """
    Execute Stage 1 for the analyst report data sources pipeline.
    This keeps execution flow centralized instead of spreading stage orchestration across multiple callers.
    """

    print_stage_banner("Stage 1 | Preparing Input Data")
    print_section_header("Loading Raw Inputs")

    raw_reports_df = read_reports_dataframe(file_path = config.raw_reports_path, max_reports = config.max_reports)
    raw_sources_df = read_alternative_sources_dataframe(file_path = config.alternative_sources_path)

    print_status(f"Loaded {len(raw_reports_df):,} report rows from {os.path.basename(config.raw_reports_path)}.")
    print_status(f"Loaded {len(raw_sources_df):,} reference rows from {os.path.basename(config.alternative_sources_path)}.")

    print_section_header("Preparing Stage Outputs")

    prepared_reports_df = prepare_reports_dataframe(raw_reports_df = raw_reports_df)
    prepared_sources_df = reshape_alternative_sources(raw_sources_df = raw_sources_df)

    reports_output_path = os.path.join(paths.stage_001_dir, "prepared_reports.csv")
    sources_output_path = os.path.join(paths.stage_001_dir, "prepared_alternative_sources.csv")

    ensure_parent_dir(reports_output_path)
    prepared_reports_df.to_csv(reports_output_path, index = False)
    prepared_sources_df.to_csv(sources_output_path, index = False)

    print_status(f"Prepared reports shape: {prepared_reports_df.shape}.")
    print_status(f"Prepared source dictionary shape: {prepared_sources_df.shape}.")
    print_status(f"Exported stage output: {os.path.basename(reports_output_path)}.")
    print_status(f"Exported stage output: {os.path.basename(sources_output_path)}.")
