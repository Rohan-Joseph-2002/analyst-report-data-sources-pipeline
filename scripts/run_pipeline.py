"""
AUTHOR: Rohan Joseph
PURPOSE: Pipeline dispatcher for stage-level execution.
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
import argparse
import subprocess




"""
Settings
"""

# --- Ensure that the src directory is on PATH ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# --- Import project-specific utilities and pipeline code ---
from project.config import DEFAULT_STAGE_ORDER, build_stage_script_map  # type: ignore
from project.utils import print_stage_banner, print_status  # type: ignore
from project.logger import capture_script_console_to_markdown  # type: ignore



"""
Script
"""

def main() -> None:
    """
    Run one stage or all stages in canonical order.
    This helps keep orchestration in Python while preserving script-level logging and isolation.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices = DEFAULT_STAGE_ORDER)
    parser.add_argument("--all", action = "store_true")
    args = parser.parse_args()

    if not args.all and not args.stage:
        raise SystemExit("Specify either --all or --stage.")

    stage_script_map = build_stage_script_map(PROJECT_ROOT)

    if args.all:
        stages_to_run = DEFAULT_STAGE_ORDER
    else:
        stages_to_run = [args.stage]

    print_stage_banner("Running Analyst Report Data Sources Pipeline")

    for stage_name in stages_to_run:
        script_path = stage_script_map[stage_name]
        print_status(f"Running stage: {stage_name}")
        subprocess.run([sys.executable, str(script_path)], cwd = PROJECT_ROOT, check = True)



"""
Main Execution
"""

if __name__ == "__main__":
    log_path = capture_script_console_to_markdown(
        run_callable = main,
        output_dir = os.path.join(PROJECT_ROOT, "output", "logs"),
        script_name = "run_pipeline",
        also_print_to_console = True,
    )
    print(f"Saved run log to: {log_path}")