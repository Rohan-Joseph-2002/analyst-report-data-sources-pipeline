"""
AUTHOR: Rohan Joseph
PURPOSE: Extract cited data sources from the prepared reports using base-phrase regex plus
         explicit-mention and fuzzy dictionary matching, writing summary and long tables.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import re
import sys
import difflib
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

PREPARED_REPORTS_PATH = os.path.join(settings.DATA_OUTPUT_DIR, "d001_prepared_reports.csv")
PREPARED_SOURCES_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d001_prepared_alternative_sources.csv"
)
SUMMARY_OUTPUT_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d002_regex_source_extraction_summary.csv"
)
LONG_OUTPUT_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d002_regex_source_extraction_long.csv"
)



# ============================================================
# Extraction Helpers
# ============================================================

def build_base_phrase_pattern():
    """
    Build the compiled regex that flags source-like phrases in report text.
    This keeps the phrase list centralized so the extractor reuses one pattern.
    """

    escaped = "|".join(re.escape(phrase) for phrase in settings.BASE_PHRASES)

    return re.compile(rf"\b(?:{escaped})\b\s*[:\-]?\s*(.+?)(?=\n|$)", flags = re.IGNORECASE)


def extract_potential_source_phrases(report_text):
    """
    Extract raw source-like phrases from report text using the base phrase pattern.
    This is the first-pass candidate generator for the rule-based extractor.
    """

    if not isinstance(report_text, str) or not report_text.strip():
        return []

    pattern = build_base_phrase_pattern()
    phrases = [normalize_whitespace(match) for match in pattern.findall(report_text)]

    return [phrase for phrase in phrases if phrase]


def clean_source_candidate(source_text):
    """
    Clean a raw candidate phrase into a compact string suitable for matching.
    This strips disclaimers and generic trailing words before dictionary linkage.
    """

    candidate = normalize_source_name(source_text)
    candidate_lower = candidate.lower()

    for disqualifier in settings.SOURCE_DISQUALIFIER_PHRASES:
        if disqualifier in candidate_lower:
            # Trim at the first disclaimer phrase so trailing narrative does not pollute matching.
            candidate = candidate[: candidate_lower.index(disqualifier)].strip()
            break

    words = candidate.split()

    while words and words[-1].lower() in settings.GENERIC_SOURCE_STOPWORDS:
        words.pop()

    return " ".join(words).strip(" -,:;")


def split_source_candidates(potential_phrases):
    """
    Split raw source phrases into atomic candidate source names.
    This turns long extracted lines into individually matchable candidates.
    """

    candidates = []

    for phrase in potential_phrases:
        normalized_phrase = normalize_whitespace(phrase)

        for split_token in settings.SOURCE_SPLIT_TOKENS:
            # Replace every recognized separator with one common token before splitting.
            normalized_phrase = normalized_phrase.replace(split_token, "|")

        for part in (clean_source_candidate(p) for p in normalized_phrase.split("|")):
            if part and len(part.split()) <= 8:
                candidates.append(part)

    return list(dict.fromkeys(candidates))


def find_explicit_dictionary_mentions(report_text, source_lookup_df):
    """
    Find exact dictionary-source mentions in the report text.
    This is the high-precision extraction pass that complements fuzzy matching.
    """

    if not isinstance(report_text, str) or not report_text.strip():
        return []

    cleaned_text = normalize_whitespace(report_text).lower()
    matched_rows = []

    for row in source_lookup_df.itertuples(index = False):
        source_name_normalized = row.source_name_normalized

        if not source_name_normalized:
            continue

        # Word-boundary match keeps this pass strict and high-precision.
        pattern = re.compile(rf"(?<!\w){re.escape(source_name_normalized.lower())}(?!\w)")
        count = len(pattern.findall(cleaned_text))

        if count <= 0:
            continue

        matched_rows.append(
            {
                "Source Name": row.source_name,
                "Source Name Normalized": source_name_normalized,
                "Source Origin": "explicit_mention",
                "Source Group": row.source_group,
                "Attention Tier": row.attention_tier,
                "Match Score": 1.0,
                "Mention Count": count,
            }
        )

    return matched_rows


def match_dictionary_sources(candidate_sources, source_lookup_df, similarity_threshold):
    """
    Match cleaned candidate sources to the prepared alternative-source dictionary.
    This links noisy extracted phrases back to curated reference entries.
    """

    best_match_by_name = {}

    for candidate_source in candidate_sources:
        normalized_candidate = normalize_source_name(candidate_source)

        if not normalized_candidate:
            continue

        for row in source_lookup_df.itertuples(index = False):
            source_name_normalized = row.source_name_normalized

            if not source_name_normalized:
                continue

            if normalized_candidate.lower() == source_name_normalized.lower():
                score = 1.0
            else:
                score = difflib.SequenceMatcher(
                    None, normalized_candidate.lower(), source_name_normalized.lower()
                ).ratio()

            if score < similarity_threshold:
                continue

            key = source_name_normalized.lower()
            existing = best_match_by_name.get(key)
            candidate_match = {
                "Source Name": row.source_name,
                "Source Name Normalized": source_name_normalized,
                "Source Origin": "dictionary_match",
                "Source Group": row.source_group,
                "Attention Tier": row.attention_tier,
                "Match Score": round(score, 4),
                "Mention Count": 1,
            }

            # Keep only the best-scoring match per reference source.
            if existing is None or candidate_match["Match Score"] > existing["Match Score"]:
                best_match_by_name[key] = candidate_match

    return list(best_match_by_name.values())


def summarize_matched_sources(matched_sources):
    """
    Convert matched source rows into compact "name {count}" labels.
    This produces readable source lists for the report-level summary CSV.
    """

    counts = {}

    for row in matched_sources:
        counts[row["Source Name"]] = counts.get(row["Source Name"], 0) + 1

    return [f"{name} {{{count}}}" if count > 1 else name for name, count in counts.items()]


def stringify_list(values):
    """
    Join a list of strings into a stable pipe-delimited string.
    This compacts list-valued fields for the summary CSV export.
    """

    return " | ".join(value for value in values if value)



# ============================================================
# Stage Builder
# ============================================================

def build_regex_stage_outputs(prepared_reports_df, prepared_sources_df, similarity_threshold):
    """
    Build the Stage-2 per-report summary and the long one-row-per-source table.
    This keeps the extraction logic testable outside the script entry point.
    """

    summary_rows = []
    long_rows = []

    for _, report_row in prepared_reports_df.iterrows():
        record = report_row.to_dict()

        potential_phrases = extract_potential_source_phrases(record["Report Text"])
        candidate_sources = split_source_candidates(potential_phrases)
        explicit_mentions = find_explicit_dictionary_mentions(
            report_text = record["Report Text Cleaned"],
            source_lookup_df = prepared_sources_df,
        )
        matched_sources = match_dictionary_sources(
            candidate_sources = candidate_sources,
            source_lookup_df = prepared_sources_df,
            similarity_threshold = similarity_threshold,
        )

        # Merge both passes into one row per source. Explicit mentions are listed first, so the
        # dict keeps the high-precision explicit hit and a source found twice is not double-counted.
        combined_by_name = {}
        for source in explicit_mentions + matched_sources:
            key = source["Source Name Normalized"].lower()
            if key not in combined_by_name:
                combined_by_name[key] = source

        explicit_labels = stringify_list(summarize_matched_sources(explicit_mentions))
        matched_labels = stringify_list(summarize_matched_sources(matched_sources))

        summary_rows.append(
            {
                "DocumentID": record["DocumentID"],
                "Year": record["Year"],
                "Date": record["Date"],
                "Contributor": record["Contributor"],
                "Report File Ticker": record["Report File Ticker"],
                "Partial Title": record["Partial Title"],
                "Pages": record["Pages"],
                "PDF File Name": record["PDF File Name"],
                "Potential Source Phrases": stringify_list(potential_phrases),
                "Regex Candidate Sources": stringify_list(candidate_sources),
                "Explicit Mentioned Sources": explicit_labels,
                "Matched Alternative Sources": matched_labels,
                "Matched Source Count": len(combined_by_name),
            }
        )

        for source in combined_by_name.values():
            long_rows.append(
                {
                    "DocumentID": record["DocumentID"],
                    "Year": record["Year"],
                    "Date": record["Date"],
                    "Contributor": record["Contributor"],
                    "Report File Ticker": record["Report File Ticker"],
                    "PDF File Name": record["PDF File Name"],
                    "Source Name": source["Source Name"],
                    "Source Name Normalized": source["Source Name Normalized"],
                    "Source Origin": source["Source Origin"],
                    "Source Group": source["Source Group"],
                    "Attention Tier": source["Attention Tier"],
                    "Match Score": source["Match Score"],
                }
            )

    summary_df = pd.DataFrame(summary_rows, columns = settings.REGEX_SUMMARY_COLUMNS)
    long_df = pd.DataFrame(long_rows, columns = settings.REGEX_LONG_COLUMNS)

    return summary_df, long_df



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Load the prepared inputs, extract sources, and write the summary and long tables.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Prepared Inputs")

    validation.require_existing_file(PREPARED_REPORTS_PATH, context = "prepared reports")
    validation.require_existing_file(PREPARED_SOURCES_PATH, context = "prepared sources")

    prepared_reports_df = io.read_csv(PREPARED_REPORTS_PATH, keep_empty_as_str = True)
    prepared_sources_df = io.read_csv(PREPARED_SOURCES_PATH, keep_empty_as_str = True)

    print_status(f"Loaded {len(prepared_reports_df)} reports, {len(prepared_sources_df)} sources.")

    print_section_header("Extracting Sources")

    summary_df, long_df = build_regex_stage_outputs(
        prepared_reports_df = prepared_reports_df,
        prepared_sources_df = prepared_sources_df,
        similarity_threshold = settings.REGEX_SIMILARITY_THRESHOLD,
    )

    io.write_csv(summary_df, SUMMARY_OUTPUT_PATH)
    io.write_csv(long_df, LONG_OUTPUT_PATH)

    print_status(f"Summary {summary_df.shape}, long {long_df.shape}.")


def main():
    """
    Run the extraction stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Data 002 | Regex Source Extraction")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "d002_regex_source_extraction",
        log_dir = settings.LOG_DIR,
    )
