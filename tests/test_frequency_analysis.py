"""
AUTHOR: Rohan Joseph
PURPOSE: Unit tests for final source-frequency analysis helpers.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from analysis.frequency_analysis import (
    build_contributor_source_frequency,
    build_source_frequency,
    build_summary_metrics,
)



"""
Tests
"""

def test_build_source_frequency_summarizes_rows() -> None:
    """
    Validate that source rows aggregate into a stable frequency table.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    source_df = pd.DataFrame(
        {
            "Source Name": ["Bloomberg", "Bloomberg", "App Annie"],
            "Source Count": [1, 1, 2],
        }
    )

    frequency_df = build_source_frequency(
        source_df = source_df,
        source_column = "Source Name",
        count_column = "Source Count",
    )

    assert frequency_df.loc[0, "Frequency"] == 2


def test_build_contributor_source_frequency_counts_mentions_by_contributor() -> None:
    """
    Validate that contributor-level source counts stay grouped and sortable.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    regex_long_df = pd.DataFrame(
        {
            "Contributor": ["Broker A", "Broker A", "Broker B"],
            "Source Name": ["Bloomberg", "Bloomberg", "App Annie"],
        }
    )

    contributor_frequency_df = build_contributor_source_frequency(regex_long_df = regex_long_df)

    assert contributor_frequency_df.loc[0, "Contributor"] == "Broker A"
    assert contributor_frequency_df.loc[0, "Frequency"] == 2


def test_build_summary_metrics_reports_regex_only_totals() -> None:
    """
    Validate that summary metrics describe only the regex pipeline outputs.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    regex_long_df = pd.DataFrame(
        {
            "DocumentID": [1, 1, 2],
            "Contributor": ["Broker A", "Broker A", "Broker B"],
            "Source Name": ["Bloomberg", "App Annie", "Bloomberg"],
        }
    )

    summary_metrics_df = build_summary_metrics(regex_long_df = regex_long_df)

    assert summary_metrics_df.loc[0, "value"] == 3
    assert summary_metrics_df.loc[1, "value"] == 2
    assert summary_metrics_df.loc[2, "metric"] == "matched_documents"
    assert summary_metrics_df.loc[2, "value"] == 2
    assert summary_metrics_df.loc[3, "metric"] == "matched_contributors"
    assert summary_metrics_df.loc[3, "value"] == 2
