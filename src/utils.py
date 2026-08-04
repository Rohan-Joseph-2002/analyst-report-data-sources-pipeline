"""
AUTHOR: Rohan Joseph
PURPOSE: Provide text-normalization and console-formatting helpers shared by two or more
         stage scripts, keeping single-use helpers out of this module.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import re



# ============================================================
# Text Normalization
# ============================================================

def normalize_whitespace(text):
    """
    Collapse repeated whitespace, newlines, and non-breaking spaces into single spaces.
    This stabilizes the regex and string matching that every downstream stage relies on.
    """

    if not isinstance(text, str):
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_source_name(text):
    """
    Normalize a source name by dropping parentheticals and special characters.
    This lets extracted candidates and dictionary entries be compared on equal footing.
    """

    text = normalize_whitespace(text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^A-Za-z0-9&.,/\- ]+", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()



# ============================================================
# Console Formatting
# ============================================================

def print_stage_banner(title):
    """
    Print a standardized banner marking the start of a pipeline stage.
    This keeps stage boundaries easy to spot in console output and captured logs.
    """

    rule = "-" * 76
    print(f"\n{rule}\n{title}\n{rule}\n")


def print_section_header(label):
    """
    Print a lightweight section header within a stage run.
    This separates the phases of a stage in the console transcript.
    """

    print(f"\n{label}")


def print_status(message):
    """
    Print a consistently indented status line.
    This makes run logs easier to scan without repeating formatting boilerplate.
    """

    print(f"  > {message}")
