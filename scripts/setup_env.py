"""
AUTHOR: Rohan Joseph
PURPOSE: Create the standard project directories for the analyst report pipeline.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
import argparse
import subprocess
import sys
import venv




"""
Settings
"""

# --- Ensure that the src directory is on PATH ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# --- Import project-specific utilities and pipeline code ---
from project.paths import PROJECT_ROOT as PACKAGE_PROJECT_ROOT  # type: ignore
from project.paths import ensure_project_directories  # type: ignore
from project.utils import print_section_header, print_stage_banner, print_status  # type: ignore
from project.logger import capture_script_console_to_markdown  # type: ignore



"""
Script
"""

def resolve_python_path(project_root: str) -> str:
    """
    Resolve the Python interpreter that should be used for dependency installation.
    This helps target the local virtual environment when it exists and otherwise fall back to the current interpreter.
    """

    venv_python_path = os.path.join(project_root, ".venv", "bin", "python")

    if os.path.exists(venv_python_path):
        return venv_python_path

    return sys.executable


def install_requirements(python_path: str, project_root: str) -> None:
    """
    Install the repository requirements using the selected interpreter.
    This helps ensure the local environment has the packages needed to run the pipeline and unit tests.
    """

    requirements_path = os.path.join(project_root, "requirements.txt")

    print_status(f"Installing requirements from: {requirements_path}")
    subprocess.run(
        [python_path, "-m", "pip", "install", "-r", requirements_path],
        cwd = project_root,
        check = True,
    )


def main() -> None:
    """
    Create the expected data and output directories for the repository and install the required packages.
    This gives the script one predictable command-line entrypoint for manual runs and repo-level orchestration.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--create-venv", action = "store_true")
    parser.add_argument("--install-project", action = "store_true")
    args = parser.parse_args()

    print_stage_banner("Setting Up Project Environment")

    paths = ensure_project_directories()

    print_section_header("Project Root")
    print_status(f"Script root: {PROJECT_ROOT}")
    print_status(f"Package root: {PACKAGE_PROJECT_ROOT}")

    print_section_header("Created or Verified Directories")
    print_status(f"Stage 1 directory: {paths.stage_001_dir}")
    print_status(f"Stage 2 directory: {paths.stage_002_dir}")
    print_status(f"Stage 3 directory: {paths.stage_003_dir}")
    print_status(f"Log directory: {paths.log_dir}")

    venv_path = os.path.join(PROJECT_ROOT, ".venv")

    if args.create_venv:
        print_section_header("Creating Virtual Environment")
        print_status(f"Creating virtual environment at: {venv_path}")
        venv.EnvBuilder(with_pip = True).create(venv_path)

    print_section_header("Installing Requirements")

    python_path = resolve_python_path(PROJECT_ROOT)
    install_requirements(python_path = python_path, project_root = PROJECT_ROOT)

    if args.install_project:
        print_section_header("Installing Project Package")
        print_status(f"Installing project with interpreter: {python_path}")
        subprocess.run(
            [python_path, "-m", "pip", "install", "-e", "."],
            cwd = PROJECT_ROOT,
            check = True,
        )

    print_section_header("Status")
    print_status("Environment setup complete.")



"""
Main Execution
"""

if __name__ == "__main__":
    log_path = capture_script_console_to_markdown(
        run_callable = main,
        output_dir = os.path.join(PROJECT_ROOT, "output", "logs"),
        script_name = "setup_env",
        also_print_to_console = True,
    )
    print(f"Saved run log to: {log_path}")
