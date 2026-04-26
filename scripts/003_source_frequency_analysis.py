"""
AUTHOR: Rohan Joseph
PURPOSE: Execute Stage 3 source frequency analysis.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-26
MODIFIED BY: OpenAI Codex
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
import sys



"""
Settings
"""

# --- Ensure that the src directory is on PATH ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# --- Import project-specific utilities and pipeline code ---
from project.env import get_runtime_config  # type: ignore
from project.logger import capture_script_console_to_markdown  # type: ignore
from project.paths import ensure_project_directories  # type: ignore
from pipelines.source_frequency_analysis import run_source_frequency_analysis  # type: ignore



"""
Script
"""

def run_stage() -> None:
    """
    Run Stage 3 using the shared runtime configuration and output directory layout.
    This keeps execution flow centralized instead of spreading stage orchestration across multiple callers.
    """

    config = get_runtime_config()
    paths = ensure_project_directories()
    run_source_frequency_analysis(config = config, paths = paths)



"""
Main Execution
"""

if __name__ == "__main__":
    log_path = capture_script_console_to_markdown(
        run_callable = run_stage,
        output_dir = os.path.join(PROJECT_ROOT, "output", "logs"),
        script_name = "003_source_frequency_analysis",
        also_print_to_console = True,
    )
    print(f"Saved run log to: {log_path}")
