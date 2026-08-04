"""
AUTHOR: Rohan Joseph
PURPOSE: Run every data/ then analysis/ script in numeric order, each in its own process, so
         the whole pipeline can be reproduced with a single command.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys
import subprocess



# ============================================================
# Functions
# ============================================================

def numbered_scripts(folder):
    """
    Return the runnable numbered scripts in a folder, sorted by filename.
    This lets run_all discover stages automatically instead of hard-coding a list.
    """

    if not os.path.isdir(folder):
        names = []
    else:
        names = sorted(n for n in os.listdir(folder) if n.endswith(".py") and not n.startswith("_"))

    return [os.path.join(folder, name) for name in names]



# ============================================================
# Main Execution
# ============================================================

def main():
    """
    Run each data/ then analysis/ script in order, each as its own process.
    This keeps a failing stage isolated and easy to locate through its own log file.
    """

    root = os.path.dirname(os.path.abspath(__file__))
    for folder in ("data", "analysis"):
        for path in numbered_scripts(os.path.join(root, folder)):
            print(f"Running {os.path.relpath(path, root)}")
            subprocess.run([sys.executable, path], check = True)


if __name__ == "__main__":
    main()
