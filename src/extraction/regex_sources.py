"""
AUTHOR: Rohan Joseph
PURPOSE: Regex and dictionary-matching helpers for analyst report data source extraction.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""

from __future__ import annotations



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import re
import difflib

from collections import Counter

import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from project.settings import (
    BASE_PHRASES,
    GENERIC_SOURCE_STOPWORDS,
    SOURCE_DISQUALIFIER_PHRASES,
    SOURCE_SPLIT_TOKENS,
)
from project.utils import normalize_source_name, normalize_whitespace



"""
Functions
"""

def build_base_phrase_pattern(base_phrases: list[str] = BASE_PHRASES) -> re.Pattern:
    """
    Build the compiled regex pattern used to identify source-like phrases in report text.
    This helps keep the phrase list centralized while letting stage code reuse one pattern.
    """

    escaped_phrases = "|".join(re.escape(phrase) for phrase in base_phrases)
    return re.compile(rf"\b(?:{escaped_phrases})\b\s*[:\-]?\s*(.+?)(?=\n|$)", flags = re.IGNORECASE)


def extract_potential_source_phrases(report_text: str) -> list[str]:
    """
    Extract raw source-like phrases from the report text using the base phrase pattern.
    Useful as the first-pass candidate generator for rule-based extraction.
    This turns source-specific text or files into structured fields that later steps can reuse directly.
    """

    if not isinstance(report_text, str) or not report_text.strip():
        return []

    pattern = build_base_phrase_pattern()
    return [normalize_whitespace(match) for match in pattern.findall(report_text) if normalize_whitespace(match)]


def clean_source_candidate(source_text: str) -> str:
    """
    Clean a raw candidate source phrase into a compact string suitable for matching.
    This helps remove disclaimers and generic trailing words before dictionary linkage.
    """

    candidate = normalize_source_name(source_text)
    candidate_lower = candidate.lower()

    for disqualifier in SOURCE_DISQUALIFIER_PHRASES:
        # Trim the candidate at the first disclaimer-style phrase so trailing narrative does not pollute matching.
        if disqualifier in candidate_lower:
            candidate = candidate[: candidate_lower.index(disqualifier)].strip()
            break

    words = candidate.split()

    while words and words[-1].lower() in GENERIC_SOURCE_STOPWORDS:
        words.pop()

    candidate = " ".join(words).strip(" -,:;")
    return candidate


def split_source_candidates(potential_phrases: list[str]) -> list[str]:
    """
    Split raw source phrases into atomic candidate source names.
    This helps convert long extracted lines into matchable source-name candidates.
    """

    candidates: list[str] = []

    for phrase in potential_phrases:
        normalized_phrase = normalize_whitespace(phrase)

        for split_token in SOURCE_SPLIT_TOKENS:
            # Replace every recognized separator with a common token before splitting the phrase into parts.
            normalized_phrase = normalized_phrase.replace(split_token, "|")

        parts = [clean_source_candidate(part) for part in normalized_phrase.split("|")]

        for part in parts:
            if not part:
                continue

            if len(part.split()) > 8:
                continue

            candidates.append(part)

    return list(dict.fromkeys(candidates))


def find_explicit_dictionary_mentions(report_text: str, source_lookup_df: pd.DataFrame) -> list[dict]:
    """
    Find exact mention matches between the report text and the prepared alternative-source dictionary.
    This helps a high-precision extraction pass alongside regex candidate matching.
    """

    if not isinstance(report_text, str) or not report_text.strip():
        return []

    cleaned_text = normalize_whitespace(report_text).lower()
    matched_rows: list[dict] = []

    for row in source_lookup_df.itertuples(index = False):
        source_name = getattr(row, "source_name")
        source_name_normalized = getattr(row, "source_name_normalized")

        if not source_name_normalized:
            continue

        # Exact mention checks are intentionally strict because this pass is meant to be the high-precision signal.
        mention_pattern = re.compile(rf"(?<!\w){re.escape(source_name_normalized.lower())}(?!\w)")
        count = len(mention_pattern.findall(cleaned_text))

        if count <= 0:
            continue

        matched_rows.append(
            {
                "Source Name": source_name,
                "Source Name Normalized": source_name_normalized,
                "Source Origin": "explicit_mention",
                "Source Group": getattr(row, "source_group"),
                "Attention Tier": getattr(row, "attention_tier"),
                "Match Score": 1.0,
                "Mention Count": count,
            }
        )

    return matched_rows


def match_dictionary_sources(
    candidate_sources: list[str],
    source_lookup_df: pd.DataFrame,
    similarity_threshold: float,
) -> list[dict]:
    """
    Match cleaned candidate sources to the prepared alternative-source dictionary.
    This helps linking noisy extracted phrases back to a curated reference list.
    """

    matched_rows: list[dict] = []
    best_match_by_name: dict[str, dict] = {}

    for candidate_source in candidate_sources:
        normalized_candidate = normalize_source_name(candidate_source)

        if not normalized_candidate:
            continue

        for row in source_lookup_df.itertuples(index = False):
            source_name_normalized = getattr(row, "source_name_normalized")

            if not source_name_normalized:
                continue

            if normalized_candidate.lower() == source_name_normalized.lower():
                score = 1.0
            else:
                # Fall back to a simple sequence-similarity score when the candidate is only approximately normalized.
                score = difflib.SequenceMatcher(
                    None,
                    normalized_candidate.lower(),
                    source_name_normalized.lower(),
                ).ratio()

            if score < similarity_threshold:
                continue

            candidate_match = {
                "Source Name": getattr(row, "source_name"),
                "Source Name Normalized": source_name_normalized,
                "Source Origin": "dictionary_match",
                "Source Group": getattr(row, "source_group"),
                "Attention Tier": getattr(row, "attention_tier"),
                "Match Score": round(score, 4),
                "Mention Count": 1,
            }

            previous_match = best_match_by_name.get(source_name_normalized.lower())

            # Keep only the best-scoring match per reference source so noisy duplicates do not inflate report output.
            if previous_match is None or candidate_match["Match Score"] > previous_match["Match Score"]:
                best_match_by_name[source_name_normalized.lower()] = candidate_match

    matched_rows.extend(best_match_by_name.values())
    return matched_rows


def summarize_matched_sources(matched_sources: list[dict]) -> list[str]:
    """
    Convert matched source rows into compact source-count labels.
    This helps report-level CSV summaries.
    """

    counts = Counter(row["Source Name"] for row in matched_sources)
    summary = []

    for source_name, count in counts.items():
        if count > 1:
            summary.append(f"{source_name} {{{count}}}")
        else:
            summary.append(source_name)

    return summary
