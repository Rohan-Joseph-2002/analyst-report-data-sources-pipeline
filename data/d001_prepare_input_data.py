"""
AUTHOR: Rohan Joseph
PURPOSE: Clean the raw analyst-report sample and reshape the wide alternative-source
         dictionary into a long lookup table, writing both to data-output for extraction.
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
from src.utils import (
    normalize_source_name,
    normalize_whitespace,
    print_section_header,
    print_stage_banner,
    print_status,
)



# ============================================================
# Settings
# ============================================================

REPORTS_INPUT_PATH = os.path.join(
    settings.INPUT_DIR, os.getenv("REPORTS_INPUT_FILE", "cleaned_reports_sample.csv")
)
ALTERNATIVE_SOURCES_INPUT_PATH = os.path.join(
    settings.INPUT_DIR, os.getenv("ALTERNATIVE_SOURCES_FILE", "alternative_sources_sample.csv")
)
PREPARED_REPORTS_PATH = os.path.join(settings.DATA_OUTPUT_DIR, "d001_prepared_reports.csv")
PREPARED_SOURCES_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d001_prepared_alternative_sources.csv"
)



# ============================================================
# Functions
# ============================================================

def truncate_text(text, limit = 180):
    """
    Truncate normalized text into a compact preview capped at `limit` characters.
    This keeps the exported preview column short enough to scan by eye.
    """

    text = normalize_whitespace(text)
    preview = text if len(text) <= limit else text[: limit - 3].rstrip() + "..."

    return preview


def prepare_reports_dataframe(raw_reports_df):
    """
    Clean and standardize the raw report sample into the prepared report schema.
    This produces a stable stage-one table that the extraction stage can rely on.
    """

    keep_columns = [c for c in raw_reports_df.columns if not str(c).startswith("Unnamed:")]
    reports = raw_reports_df[keep_columns].copy()
    validation.require_columns(reports, settings.REPORT_REQUIRED_COLUMNS, context = "raw reports")

    reports["Report Text"] = reports["Report Text"].fillna("").astype(str)
    reports["Report Text Cleaned"] = reports["Report Text"].map(normalize_whitespace)
    reports["Report Text Preview"] = reports["Report Text Cleaned"].map(truncate_text)
    reports["Report Word Count"] = reports["Report Text Cleaned"].map(
        lambda text: len(text.split())
    )

    return reports[settings.PREPARED_REPORT_COLUMNS].copy()


def reshape_alternative_sources(raw_sources_df):
    """
    Convert the wide alternative-source dictionary into a long, de-duplicated lookup table.
    This makes explicit-mention and fuzzy matching straightforward in the extraction stage.
    """

    prepared_rows = []

    for column_name, column_metadata in settings.ALTERNATIVE_SOURCE_COLUMN_MAP.items():
        if column_name not in raw_sources_df.columns:
            continue

        for raw_value in raw_sources_df[column_name].dropna().tolist():
            source_name = normalize_whitespace(str(raw_value))
            source_name_normalized = normalize_source_name(source_name)

            if not source_name or not source_name_normalized:
                continue

            if source_name_normalized.lower() in settings.REFERENCE_SOURCE_EXCLUSIONS:
                continue

            prepared_rows.append(
                {
                    "source_name": source_name,
                    "source_name_normalized": source_name_normalized,
                    "source_group": column_metadata["source_group"],
                    "attention_tier": column_metadata["attention_tier"],
                }
            )

    prepared = pd.DataFrame(prepared_rows).drop_duplicates().reset_index(drop = True)

    if prepared.empty:
        return pd.DataFrame(columns = settings.PREPARED_SOURCE_COLUMNS)

    # Rank so the highest-attention, company-first entry wins when a name repeats.
    attention_rank = {"ATT = 1": 0, "0 < ATT < 1": 1, "ATT = 0": 2}
    group_rank = {"alternative_company_name": 0, "alternative_product_name": 1}
    prepared["attention_rank"] = prepared["attention_tier"].map(attention_rank).fillna(9)
    prepared["source_group_rank"] = prepared["source_group"].map(group_rank).fillna(9)

    prepared = (
        prepared.sort_values(
            by = ["source_name_normalized", "attention_rank", "source_group_rank", "source_name"],
        )
        .drop_duplicates(subset = ["source_name_normalized"], keep = "first")
        .reset_index(drop = True)
    )

    return prepared[settings.PREPARED_SOURCE_COLUMNS].copy()



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Load the raw inputs, prepare the reports and source dictionary, and write them to data-output.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Raw Inputs")

    validation.require_existing_file(REPORTS_INPUT_PATH, context = "reports")
    validation.require_existing_file(ALTERNATIVE_SOURCES_INPUT_PATH, context = "sources")

    raw_reports_df = io.read_csv(REPORTS_INPUT_PATH).head(settings.MAX_REPORTS).copy()
    raw_sources_df = io.read_csv(ALTERNATIVE_SOURCES_INPUT_PATH)

    print_status(f"Loaded {len(raw_reports_df)} reports and {len(raw_sources_df)} references.")

    print_section_header("Preparing Stage Outputs")

    prepared_reports_df = prepare_reports_dataframe(raw_reports_df)
    prepared_sources_df = reshape_alternative_sources(raw_sources_df)

    io.write_csv(prepared_reports_df, PREPARED_REPORTS_PATH)
    io.write_csv(prepared_sources_df, PREPARED_SOURCES_PATH)

    print_status(f"Reports {prepared_reports_df.shape}, sources {prepared_sources_df.shape}.")


def main():
    """
    Run the prepare-input stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Data 001 | Prepare Input Data")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "d001_prepare_input_data",
        log_dir = settings.LOG_DIR,
    )
