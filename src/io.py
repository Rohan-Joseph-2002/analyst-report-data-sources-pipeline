"""
AUTHOR: Rohan Joseph
PURPOSE: Provide small, safe helpers for reading and writing CSV and text files so that
         every stage loads and saves data the same predictable way.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import pandas as pd



# ============================================================
# Functions
# ============================================================

def read_csv(path, keep_empty_as_str = False):
    """
    Read a CSV file into a DataFrame, optionally keeping blank cells as "".
    This gives every stage one predictable, well-behaved way to load tabular input.
    """

    if keep_empty_as_str:
        frame = pd.read_csv(path, keep_default_na = False, na_values = [])
    else:
        frame = pd.read_csv(path)

    return frame


def write_csv(df, path):
    """
    Write a DataFrame to CSV, creating the parent folder if it does not exist.
    This lets stages save results without each one repeating folder-creation logic.
    """

    os.makedirs(os.path.dirname(path), exist_ok = True)
    df.to_csv(path, index = False)

    return path


def read_text(path):
    """
    Read a UTF-8 text file into a single string.
    This centralizes text loading so encoding handling stays consistent everywhere.
    """

    with open(path, encoding = "utf-8") as handle:
        text = handle.read()

    return text


def write_text(text, path):
    """
    Write a string to a UTF-8 text file, creating the parent folder if it does not exist.
    This lets stages save reports and logs without each one repeating folder-creation logic.
    """

    os.makedirs(os.path.dirname(path), exist_ok = True)
    with open(path, "w", encoding = "utf-8") as handle:
        handle.write(text)

    return path
