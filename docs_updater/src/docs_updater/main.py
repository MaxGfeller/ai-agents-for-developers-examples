#!/usr/bin/env python
import warnings
import subprocess
import os

from docs_updater.crew import docs_updater_crew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# Dynamically get the git diff from the example-app directory
example_app_dir = os.path.join(os.path.dirname(__file__), '../../example-app')
try:
    diff = subprocess.check_output(
        ['git', 'diff'],
        cwd=example_app_dir,
        stderr=subprocess.STDOUT
    ).decode('utf-8')
except Exception as e:
    diff = f"[Error running git diff: {e}]"

if not diff.strip():
    diff = ""

def run():
    """
    Run the crew.
    """
    inputs = {
        'diff': diff
    }
    docs_updater_crew.kickoff(inputs=inputs)


if __name__ == "__main__":
    run()