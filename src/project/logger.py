"""
AUTHOR: Rohan Joseph
PURPOSE: Execution logging utilities for capturing stdout and stderr to Markdown.
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
import datetime



"""
Classes
"""

class _TeeStream:
    """
    Write to multiple file-like streams at the same time.
    This helps preserve console visibility while also writing deterministic run logs to disk.
    """

    def __init__(self, streams):
        """
        Store the underlying streams that should receive mirrored output.
        This keeps the tee wrapper lightweight while the logger decides where output should go.
        """
        self.streams = streams

    def write(self, data):
        """
        Forward text to every target stream and keep them flushed in step.
        This mirrors each chunk of output to every configured destination.
        """
        for stream in self.streams:
            try:
                stream.write(data)
            except Exception:
                pass
        # Flush after each write so console output and Markdown logs stay synchronized.
        self.flush()

    def flush(self):
        """
        Flush each underlying stream when it supports flushing.
        This keeps console and file destinations synchronized during long script runs.
        """
        for stream in self.streams:
            try:
                stream.flush()
            except Exception:
                pass


"""
Functions
"""

def capture_script_console_to_markdown(
    run_callable,
    output_dir = "output/logs",
    script_name = None,
    also_print_to_console = True,
) -> str:
    """
    Capture stdout and stderr produced during a single callable execution into a Markdown file.
    This helps preserve a complete run transcript for later debugging, review, and reproducibility.
    """

    os.makedirs(output_dir, exist_ok = True)

    safe_name = script_name if script_name is not None else "script_run"
    md_path = os.path.join(output_dir, f"{safe_name}.md")

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    markdown_file = None

    try:
        markdown_file = open(md_path, "w", encoding = "utf-8")

        if also_print_to_console:
            # Mirror output to the console while simultaneously writing the Markdown transcript.
            sys.stdout = _TeeStream([original_stdout, markdown_file])
            sys.stderr = _TeeStream([original_stderr, markdown_file])
        else:
            sys.stdout = markdown_file
            sys.stderr = markdown_file

        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"# Script run log: {safe_name}")
        print("")
        print(f"- **Start:** {start_time}")
        print("")
        print("```text")

        run_callable()

        print("```")
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("")
        print(f"- **End:** {end_time}")

    except Exception:
        try:
            print("```")
        except Exception:
            pass
        raise

    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        if markdown_file is not None:
            try:
                markdown_file.close()
            except Exception:
                pass

    return md_path
