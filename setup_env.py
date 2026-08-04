"""
AUTHOR: Rohan Joseph
PURPOSE: Create the virtual environment, install dependencies, and copy .env from the example
         so a fresh clone becomes a runnable checkout with one command.
DATE CREATED: 2026-07-27
DATE MODIFIED: 2026-07-27
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys
import shutil
import subprocess



# ============================================================
# Functions
# ============================================================

def copy_env_file(root):
    """
    Create .env from .env.example when .env does not already exist.
    This gives contributors working defaults without overwriting their local settings.
    """

    env_path = os.path.join(root, ".env")
    example_path = os.path.join(root, ".env.example")
    if os.path.isfile(env_path):
        print(".env already exists")

        return
    if os.path.isfile(example_path):
        shutil.copyfile(example_path, env_path)
        print("Created .env from .env.example")


def create_venv_and_install(root):
    """
    Create the .venv environment and install runtime and dev dependencies into it.
    This turns a fresh clone into a working checkout using POSIX venv paths.
    """

    venv_dir = os.path.join(root, ".venv")
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check = True)
    pip = os.path.join(venv_dir, "bin", "pip")
    requirements = ["-r", "requirements.txt", "-r", "requirements-dev.txt"]
    subprocess.run([pip, "install", *requirements], check = True)



# ============================================================
# Main Execution
# ============================================================

def main():
    """
    Copy the env file and build the virtual environment for the repo.
    This gives one command from a fresh clone to a working setup.
    """

    root = os.path.dirname(os.path.abspath(__file__))
    copy_env_file(root)
    create_venv_and_install(root)
    print("Setup complete. Activate with: source .venv/bin/activate")


if __name__ == "__main__":
    main()
