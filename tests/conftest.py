"""
AUTHOR: Rohan Joseph
PURPOSE: Configure the test environment for repository-level imports.
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

# --- Ensure that the src directory is on PATH for test imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


"""
Pytest Hooks
"""

def _write_flow_line(config, message: str) -> None:
    """
    Write one flow line through pytest's terminal reporter when available.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    terminal_reporter = config.pluginmanager.getplugin("terminalreporter")

    if terminal_reporter is not None:
        terminal_reporter.write_line(message)
    else:
        print(message)


def pytest_configure(config) -> None:
    """
    Disable stdout capture so test-flow messages stay visible during normal pytest runs.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    config.option.capture = "no"


def pytest_sessionstart(session) -> None:
    """
    Print a short banner at the start of the repository test session.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    _write_flow_line(session.config, "\n=== Starting analyst-report-data-sources-pipeline test session ===")


def pytest_runtest_setup(item) -> None:
    """
    Print the test identifier before each test runs.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    _write_flow_line(item.config, f"\n--- Running test: {item.nodeid}")


def pytest_runtest_teardown(item, nextitem) -> None:
    """
    Print the test identifier after each test completes.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    _write_flow_line(item.config, f"--- Finished test: {item.nodeid}")


def pytest_sessionfinish(session, exitstatus) -> None:
    """
    Print a short summary banner at the end of the repository test session.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """

    _write_flow_line(session.config, f"\n=== Finished analyst-report-data-sources-pipeline test session (exit={exitstatus}) ===")
