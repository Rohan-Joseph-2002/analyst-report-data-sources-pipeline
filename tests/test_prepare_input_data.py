"""
AUTHOR: Rohan Joseph
PURPOSE: Unit tests for Stage 1 input preparation logic.
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
from pipelines.prepare_input_data import (
    prepare_reports_dataframe,
    reshape_alternative_sources,
)



"""
Tests
"""

def test_prepare_reports_dataframe_adds_clean_columns() -> None:
    """
    Validate that Stage 1 report preparation removes unnamed columns and adds cleaned text fields.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    raw_reports_df = pd.DataFrame(
        {
            "Unnamed: 0": [0],
            "DocumentID": [1],
            "Date": ["2021-01-01"],
            "Year": [2021],
            "Contributor": ["Example Broker"],
            "Report File Ticker": ["ABCD.N"],
            "Partial Title": ["Example Title"],
            "Pages": [12],
            "PDF File Name": ["example.pdf"],
            "Report Text": ["Source: Bloomberg\nSource: App Annie"],
        }
    )

    prepared_reports_df = prepare_reports_dataframe(raw_reports_df = raw_reports_df)

    assert "Unnamed: 0" not in prepared_reports_df.columns
    assert "Report Text Cleaned" in prepared_reports_df.columns
    assert prepared_reports_df.loc[0, "Report Word Count"] > 0


def test_reshape_alternative_sources_creates_long_dictionary() -> None:
    """
    Validate that the alternative-source dictionary is reshaped into the expected long format.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    raw_sources_df = pd.DataFrame(
        {
            "List of Alternative Company Names | ATT = 1": ["Bloomberg"],
            "List of Alternative Product Names | ATT = 1": [None],
            "List of Alternative Company Names | 0 < ATT < 1": [None],
            "List of Alternative Product Names | 0 < ATT < 1": ["App Annie"],
            "List of Alternative Company Names | ATT = 0": [None],
            "List of Alternative Product Names | ATT = 0": [None],
        }
    )

    prepared_sources_df = reshape_alternative_sources(raw_sources_df = raw_sources_df)

    assert len(prepared_sources_df) == 2
    assert set(prepared_sources_df["source_group"]) == {"alternative_company_name", "alternative_product_name"}
