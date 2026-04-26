"""
AUTHOR: Rohan Joseph
PURPOSE: Central repository configuration and stage registry.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os



"""
Settings
"""

APP_NAME = "analyst_report_data_sources_pipeline"

DEFAULT_STAGE_ORDER = [
    "001_prepare_input_data",
    "002_regex_source_extraction",
    "003_source_frequency_analysis",
]



"""
Functions
"""

def build_stage_script_map(project_root: str) -> dict[str, str]:
    """
    Build the canonical stage-to-script mapping for the repository.
    This helps keep orchestration logic centralized and avoid duplicated script references.
    """

    scripts_dir = os.path.join(project_root, "scripts")

    return {
        "001_prepare_input_data": os.path.join(scripts_dir, "001_prepare_input_data.py"),
        "002_regex_source_extraction": os.path.join(scripts_dir, "002_regex_source_extraction.py"),
        "003_source_frequency_analysis": os.path.join(scripts_dir, "003_source_frequency_analysis.py"),
    }
