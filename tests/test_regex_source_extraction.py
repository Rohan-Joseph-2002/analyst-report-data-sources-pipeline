"""
AUTHOR: Rohan Joseph
PURPOSE: Unit tests for regex source extraction helpers.
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
from extraction.regex_sources import (
    extract_potential_source_phrases,
    find_explicit_dictionary_mentions,
    match_dictionary_sources,
    split_source_candidates,
)



"""
Tests
"""

def test_extract_potential_source_phrases_finds_source_lines() -> None:
    """
    Validate that source-like lines are extracted from report text.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    report_text = "Source: Bloomberg\nAccording to App Annie\nNo source here"
    potential_phrases = extract_potential_source_phrases(report_text = report_text)

    assert "Bloomberg" in potential_phrases
    assert "App Annie" in potential_phrases


def test_split_source_candidates_breaks_apart_delimited_sources() -> None:
    """
    Validate that delimited source phrases split into atomic candidates.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    candidates = split_source_candidates(["Bloomberg, App Annie and Similarweb"])
    assert "Bloomberg" in candidates
    assert "App Annie" in candidates
    assert "Similarweb" in candidates


def test_dictionary_matching_finds_reference_sources() -> None:
    """
    Validate that cleaned candidate sources match the prepared reference dictionary.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    source_lookup_df = pd.DataFrame(
        [
            {
                "source_name": "Bloomberg",
                "source_name_normalized": "Bloomberg",
                "source_group": "alternative_company_name",
                "attention_tier": "ATT = 1",
            }
        ]
    )

    matched_sources = match_dictionary_sources(
        candidate_sources = ["Bloomberg"],
        source_lookup_df = source_lookup_df,
        similarity_threshold = 0.88,
    )

    assert matched_sources[0]["Source Name"] == "Bloomberg"


def test_explicit_dictionary_mentions_count_sources_in_text() -> None:
    """
    Validate that exact mentions are found in the cleaned report text.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    source_lookup_df = pd.DataFrame(
        [
            {
                "source_name": "Bloomberg",
                "source_name_normalized": "Bloomberg",
                "source_group": "alternative_company_name",
                "attention_tier": "ATT = 1",
            }
        ]
    )

    explicit_mentions = find_explicit_dictionary_mentions(
        report_text = "Bloomberg data was used. Bloomberg was cited again.",
        source_lookup_df = source_lookup_df,
    )

    assert explicit_mentions[0]["Mention Count"] == 2
