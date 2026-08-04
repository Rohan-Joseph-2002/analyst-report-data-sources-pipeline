"""
AUTHOR: Rohan Joseph
PURPOSE: Test the Stage 2 extraction helpers and the stage builder, including the fix that
         stops a source matched by both passes from being double-counted.
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
from data.d002_regex_source_extraction import (
    build_regex_stage_outputs,
    extract_potential_source_phrases,
    find_explicit_dictionary_mentions,
    match_dictionary_sources,
    split_source_candidates,
)



# ============================================================
# Tests
# ============================================================

def test_extract_potential_source_phrases_finds_source_lines():
    """
    Check that source-like lines are extracted from report text.
    This locks the behavior of the first-pass candidate generator.
    """

    phrases = extract_potential_source_phrases("Source: Bloomberg\nAccording to Demo Analytics")

    assert any("Bloomberg" in phrase for phrase in phrases)
    assert any("Demo Analytics" in phrase for phrase in phrases)


def test_split_source_candidates_breaks_delimited_sources():
    """
    Check that delimited source phrases split into atomic candidates.
    This locks the candidate-splitting behavior the matcher relies on.
    """

    candidates = split_source_candidates(["Bloomberg, Demo Analytics and Example Insights"])

    assert "Bloomberg" in candidates
    assert "Demo Analytics" in candidates
    assert "Example Insights" in candidates


def test_dictionary_matching_links_candidate_to_reference():
    """
    Check that a cleaned candidate matches its reference dictionary entry.
    This locks the fuzzy/exact dictionary-matching pass.
    """

    lookup = pd.DataFrame(
        [
            {
                "source_name": "Demo Analytics", "source_name_normalized": "Demo Analytics",
                "source_group": "alternative_company_name", "attention_tier": "ATT = 1",
            }
        ]
    )

    matched = match_dictionary_sources(["Demo Analytics"], lookup, similarity_threshold = 0.88)

    assert matched[0]["Source Name"] == "Demo Analytics"


def test_explicit_mentions_count_occurrences():
    """
    Check that exact dictionary mentions are counted in the cleaned report text.
    This locks the high-precision explicit-mention pass.
    """

    lookup = pd.DataFrame(
        [
            {
                "source_name": "Demo Analytics", "source_name_normalized": "Demo Analytics",
                "source_group": "alternative_company_name", "attention_tier": "ATT = 1",
            }
        ]
    )

    text = "Demo Analytics led. Demo Analytics again."
    mentions = find_explicit_dictionary_mentions(text, lookup)

    assert mentions[0]["Mention Count"] == 2


def test_build_outputs_dedupes_source_matched_by_both_passes():
    """
    Check that a source found by both the explicit and fuzzy passes yields one long row.
    This guards against the double-counting bug fixed during the overhaul.
    """

    reports = pd.DataFrame(
        [
            {
                "DocumentID": "DOC1", "Year": 2024, "Date": "2024-01-01", "Contributor": "Alpha",
                "Report File Ticker": "X.N", "Partial Title": "Title", "Pages": 1,
                "PDF File Name": "x.pdf",
                "Report Text": "According to Demo Analytics, results improved.",
                "Report Text Cleaned": "According to Demo Analytics, results improved.",
            }
        ]
    )
    sources = pd.DataFrame(
        [
            {
                "source_name": "Demo Analytics", "source_name_normalized": "Demo Analytics",
                "source_group": "alternative_company_name", "attention_tier": "ATT = 1",
            }
        ]
    )

    summary_df, long_df = build_regex_stage_outputs(reports, sources, similarity_threshold = 0.88)
    demo_rows = long_df[long_df["Source Name"] == "Demo Analytics"]

    assert len(demo_rows) == 1
    assert summary_df.loc[0, "Matched Source Count"] == 1



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
        script_name = "t002_regex_source_extraction",
        log_dir = settings.LOG_DIR,
    )
