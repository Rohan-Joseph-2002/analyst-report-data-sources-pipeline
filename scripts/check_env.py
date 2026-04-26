"""
AUTHOR: Rohan Joseph
PURPOSE: Verify the runtime environment and required local input files.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
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
from project.paths import ensure_project_directories  # type: ignore
from project.utils import print_section_header, print_status, print_stage_banner  # type: ignore
from project.validation import require_existing_file  # type: ignore
from project.logger import capture_script_console_to_markdown  # type: ignore



"""
Script
"""

def main() -> None:
    """
    Check that the configured local runtime inputs exist and that output directories can be created.
    This gives the script one predictable command-line entrypoint for manual runs and repo-level orchestration.
    """

    print_stage_banner("Checking Runtime Environment")

    config = get_runtime_config()
    paths = ensure_project_directories()

    require_existing_file(config.raw_reports_path, "raw reports file")
    require_existing_file(config.alternative_sources_path, "alternative sources file")

    print_section_header("Resolved Configuration")
    print_status(f"Runtime mode: {config.runtime_mode}")
    print_status(f"Raw reports path: {config.raw_reports_path}")
    print_status(f"Alternative sources path: {config.alternative_sources_path}")
    print_status(f"Regex similarity threshold: {config.regex_similarity_threshold}")
    print_status(f"Max reports: {config.max_reports}")

    print_section_header("Output Directories")
    print_status(f"Stage 1 directory: {paths.stage_001_dir}")
    print_status(f"Stage 2 directory: {paths.stage_002_dir}")
    print_status(f"Stage 3 directory: {paths.stage_003_dir}")
    print_status(f"Log directory: {paths.log_dir}")

    print_section_header("Status")
    print_status("Environment check passed.")



"""
Main Execution
"""

if __name__ == "__main__":
    log_path = capture_script_console_to_markdown(
        run_callable = main,
        output_dir = os.path.join(PROJECT_ROOT, "output", "logs"),
        script_name = "check_env",
        also_print_to_console = True,
    )
    print(f"Saved run log to: {log_path}")
