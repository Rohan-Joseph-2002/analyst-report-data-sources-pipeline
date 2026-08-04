"""
AUTHOR: Rohan Joseph
PURPOSE: Mirror a script's console output into a timestamped Markdown log file so that
         every run leaves an inspectable record without changing how the script prints.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys

from io import StringIO
from datetime import UTC, datetime



# ============================================================
# Console Capture
# ============================================================

class _Tee:
    """
    Write to several streams at once so output reaches both the console and a buffer.
    This is a private class used by capture_script_console_to_markdown to mirror console output.
    """

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        """
        Write the given text to every wrapped stream.
        This lets a single print reach both the live console and the captured log.
        """

        for stream in self.streams:
            stream.write(text)

        return len(text)

    def flush(self):
        """
        Flush every wrapped stream.
        This ensures buffered output is not lost if the script exits abruptly.
        """

        for stream in self.streams:
            stream.flush()


def capture_script_console_to_markdown(run_callable, script_name, log_dir):
    """
    Run the given callable while mirroring its console output into logs/<script_name>.md.
    This gives every script an inspectable run log without changing how it prints.
    """

    os.makedirs(log_dir, exist_ok = True)

    log_path = os.path.join(log_dir, f"{script_name}.md")

    buffer = StringIO()
    old_out, old_err = sys.stdout, sys.stderr

    sys.stdout = _Tee(old_out, buffer)
    sys.stderr = _Tee(old_err, buffer)

    try:
        run_callable()

    finally:
        sys.stdout, sys.stderr = old_out, old_err

        stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        body = buffer.getvalue()

        with open(log_path, "w", encoding = "utf-8") as handle:
            handle.write(f"# {script_name}\n\n_run: {stamp}_\n\n```text\n{body}\n```\n")
