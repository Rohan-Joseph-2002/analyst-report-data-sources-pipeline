"""
AUTHOR: Rohan Joseph
PURPOSE: Shared utility functions for formatting, normalization, and diagnostics.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
import re




"""
Functions
"""

def print_section_header(label: str) -> None:
    """
    Print a lightweight section header within a stage run.
    This helps separate report-level or file-level work in the console transcript.
    """

    print(f"\n{label}")


def print_status(message: str) -> None:
    """
    Print a consistently indented status line.
    This helps make logs easier to scan without repeating formatting boilerplate.
    """

    print(f"  > {message}")


def print_stage_banner(label: str) -> None:
    """
    Print a standardized banner for a pipeline stage.
    This helps make run logs easier to scan.
    """

    print("\n" + "-" * 76)
    print(label)
    print("-" * 76 + "\n")


def ensure_parent_dir(file_path: str) -> None:
    """
    Ensure that a file's parent directory exists before writing.
    This helps avoid repeated parent-directory creation code in export steps.
    """

    os.makedirs(os.path.dirname(file_path), exist_ok = True)


def normalize_whitespace(text: str) -> str:
    """
    Normalize repeated whitespace, newlines, and non-breaking spaces in text.
    This helps stabilize downstream regex and string matching.
    """

    if not isinstance(text, str):
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_text(text: str, limit: int = 180) -> str:
    """
    Truncate long text into a compact preview.
    This helps export previews and README examples.
    """

    text = normalize_whitespace(text)

    if len(text) <= limit:
        return text

    return text[: limit - 3].rstrip() + "..."


def normalize_source_name(text: str) -> str:
    """
    Normalize a source name by removing special characters and collapsing whitespace.
    This helps exact and fuzzy matching between extracted candidates and reference dictionaries.
    """

    text = normalize_whitespace(text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^A-Za-z0-9&.,/\- ]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def stringify_list(values: list[str]) -> str:
    """
    Convert a list of strings into a stable pipe-delimited string.
    This helps compact CSV summary exports.
    """

    cleaned_values = [value for value in values if value]
    return " | ".join(cleaned_values)
