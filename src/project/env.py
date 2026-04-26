"""
AUTHOR: Rohan Joseph
PURPOSE: Environment loading and runtime configuration validation.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""

from __future__ import annotations



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
from dataclasses import dataclass


# --- Import project-specific utilities and pipeline code ---
from project.paths import PROJECT_ROOT
from project.settings import (
    DEFAULT_MAX_REPORTS,
    DEFAULT_REGEX_SIMILARITY_THRESHOLD,
)



"""
Settings
"""

ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
DEFAULT_RAW_REPORTS_PATH = os.path.join("input", "lseg_workspace_sample", "sample_cleaned_lseg_reports.csv")
DEFAULT_ALTERNATIVE_SOURCES_PATH = os.path.join("input", "reference", "alternative_data_sources_sample.csv")



"""
Classes
"""

@dataclass(frozen = True)
class RuntimeConfig:
    """
    Typed runtime configuration for the repository.
    This gives the rest of the repository one typed source of runtime settings and paths.
    """

    runtime_mode: str
    raw_reports_path: str
    alternative_sources_path: str
    regex_similarity_threshold: float
    max_reports: int



"""
Functions
"""

def load_dotenv_file(env_path: str = ENV_FILE) -> None:
    """
    Load key-value pairs from a local .env file into the process environment.
    This helps keep the repository self-contained without requiring external dotenv packages.
    """

    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding = "utf-8") as handle:
        raw_lines = handle.readlines()

    for raw_line in raw_lines:
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key and key not in os.environ:
            # Respect any variables the caller already supplied while still honoring repo-local defaults.
            os.environ[key] = value


def resolve_project_path(path_value: str | None, default_path: str) -> str:
    """
    Resolve a configured path relative to the project root when needed.
    This helps support portable local defaults without forcing absolute paths in .env files.
    """

    if path_value is None:
        return os.path.abspath(os.path.join(PROJECT_ROOT, default_path))

    candidate_path = os.path.expanduser(path_value)

    if os.path.isabs(candidate_path):
        return os.path.abspath(candidate_path)

    return os.path.abspath(os.path.join(PROJECT_ROOT, candidate_path))


def get_runtime_config() -> RuntimeConfig:
    """
    Build the runtime configuration from environment variables and .env.
    This helps standardize path handling and stage behavior across entry scripts.
    """

    load_dotenv_file()

    # Assemble one typed config object so every script resolves paths and thresholds the same way.
    return RuntimeConfig(
        runtime_mode = os.environ.get("RUNTIME_MODE", "local"),
        raw_reports_path = resolve_project_path(
            path_value = os.environ.get("RAW_REPORTS_PATH"),
            default_path = DEFAULT_RAW_REPORTS_PATH,
        ),
        alternative_sources_path = resolve_project_path(
            path_value = os.environ.get("ALTERNATIVE_SOURCES_PATH"),
            default_path = DEFAULT_ALTERNATIVE_SOURCES_PATH,
        ),
        regex_similarity_threshold = float(
            os.environ.get("REGEX_SIMILARITY_THRESHOLD", str(DEFAULT_REGEX_SIMILARITY_THRESHOLD))
        ),
        max_reports = int(os.environ.get("MAX_REPORTS", str(DEFAULT_MAX_REPORTS))),
    )
