"""
AUTHOR: Rohan Joseph
PURPOSE: Unit tests for environment-template helpers.
DATE CREATED: 2026-04-26
DATE MODIFIED: 2026-04-26
MODIFIED BY: OpenAI Codex
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os


# --- Import project-specific utilities and pipeline code ---
from project.env import ensure_env_file



"""
Tests
"""

def test_ensure_env_file_copies_example_when_missing(tmp_path) -> None:
    """
    Validate that the setup helper creates a local .env from the tracked template.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    env_path = os.path.join(tmp_path, ".env")
    example_path = os.path.join(tmp_path, ".env.example")

    with open(example_path, "w", encoding = "utf-8") as handle:
        handle.write("RUNTIME_MODE=local\nMAX_REPORTS=15\n")

    created = ensure_env_file(env_path = env_path, example_path = example_path)

    assert created is True

    with open(env_path, "r", encoding = "utf-8") as handle:
        assert handle.read() == "RUNTIME_MODE=local\nMAX_REPORTS=15\n"


def test_ensure_env_file_preserves_existing_local_config(tmp_path) -> None:
    """
    Validate that the setup helper does not overwrite an existing local .env file.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    env_path = os.path.join(tmp_path, ".env")
    example_path = os.path.join(tmp_path, ".env.example")

    with open(example_path, "w", encoding = "utf-8") as handle:
        handle.write("RUNTIME_MODE=local\n")

    with open(env_path, "w", encoding = "utf-8") as handle:
        handle.write("RUNTIME_MODE=custom\n")

    created = ensure_env_file(env_path = env_path, example_path = example_path)

    assert created is False

    with open(env_path, "r", encoding = "utf-8") as handle:
        assert handle.read() == "RUNTIME_MODE=custom\n"
