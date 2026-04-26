"""
AUTHOR: Rohan Joseph
PURPOSE: Convenience wrapper for running all pipeline stages in canonical order.
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
import subprocess




"""
Settings
"""

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# --- Import project-specific utilities and pipeline code ---
from project.logger import capture_script_console_to_markdown  # type: ignore



"""
Script
"""

def main() -> None:
    """
    Run the full repository pipeline through the standard Python dispatcher.
    This gives the script one predictable command-line entrypoint for manual runs and repo-level orchestration.
    """

    print("=== Running analyst-report-data-sources-pipeline full workflow ===")
    print(f"Project root: {PROJECT_ROOT}")
    print("Delegating to scripts/run_pipeline.py --all")

    subprocess.run(
        [sys.executable, str(os.path.join(PROJECT_ROOT, "scripts", "run_pipeline.py")), "--all"],
        cwd = PROJECT_ROOT,
        check = True,
    )

    print("=== Finished analyst-report-data-sources-pipeline full workflow ===")



"""
Main Execution
"""

if __name__ == "__main__":
    log_path = capture_script_console_to_markdown(
        run_callable = main,
        output_dir = os.path.join(PROJECT_ROOT, "output", "logs"),
        script_name = "00A_run_all",
        also_print_to_console = True,
    )
    print(f"Saved run log to: {log_path}")
