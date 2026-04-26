"""
AUTHOR: Rohan Joseph
PURPOSE: Frequency summaries for regex-based source extraction outputs.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-26
MODIFIED BY: OpenAI Codex
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import pandas as pd



"""
Functions
"""

def build_source_frequency(source_df: pd.DataFrame, source_column: str, count_column: str) -> pd.DataFrame:
    """
    Build a frequency table for extracted sources.
    This helps summarize which sources appear most often across the regex extraction output.
    """

    if source_df.empty:
        return pd.DataFrame(columns = ["Source Name", "Frequency"])

    frequency_df = (
        source_df.groupby(source_column, as_index = False)[count_column]
        .sum()
        .rename(columns = {source_column: "Source Name", count_column: "Frequency"})
        .sort_values(by = ["Frequency", "Source Name"], ascending = [False, True])
        .reset_index(drop = True)
    )

    return frequency_df


def build_contributor_source_frequency(regex_long_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a contributor-by-source frequency table from the regex long output.
    This helps identifying which contributors cite which data sources most often.
    """

    if regex_long_df.empty:
        return pd.DataFrame(columns = ["Contributor", "Source Name", "Frequency"])

    return (
        regex_long_df.groupby(["Contributor", "Source Name"], as_index = False)
        .size()
        .rename(columns = {"size": "Frequency"})
        .sort_values(by = ["Frequency", "Contributor", "Source Name"], ascending = [False, True, True])
        .reset_index(drop = True)
    )


def build_summary_metrics(regex_long_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build compact summary metrics for the final analysis stage.
    Useful as a top-level review table after the pipeline finishes.
    This creates one standardized intermediate object that downstream stages can consume directly.
    """

    metrics = [
        {
            "section": "regex_stage",
            "metric": "row_count",
            "value": int(len(regex_long_df)),
            "notes": "Total regex long-output rows.",
        },
        {
            "section": "regex_stage",
            "metric": "unique_sources",
            "value": int(regex_long_df["Source Name"].nunique()) if not regex_long_df.empty else 0,
            "notes": "Unique sources identified by the regex stage.",
        },
        {
            "section": "regex_stage",
            "metric": "matched_documents",
            "value": int(regex_long_df["DocumentID"].nunique()) if not regex_long_df.empty else 0,
            "notes": "Unique reports with at least one extracted source.",
        },
        {
            "section": "regex_stage",
            "metric": "matched_contributors",
            "value": int(regex_long_df["Contributor"].nunique()) if not regex_long_df.empty else 0,
            "notes": "Contributors with at least one extracted source mention.",
        },
    ]

    return pd.DataFrame(metrics)
