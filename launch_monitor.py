#!/usr/bin/env python3
"""
ScoreBlocker Monitor Launcher
Closes all existing instances and launches two ScoreBlocker windows using specified config
"""

import sys
import os
import subprocess
import time
import argparse


def launch_monitor_setup(config_file):
    """
    Close all existing ScoreBlocker instances and launch two new ones
    using the specified configuration file
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    score_blocker_script = os.path.join(script_dir, 'score_blocker.py')

    # Make config_file path absolute if it's relative
    if not os.path.isabs(config_file):
        config_file = os.path.join(script_dir, config_file)

    # Verify config file exists
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)

    print(f"Launching ScoreBlocker with config: {config_file}")

    # Step 1: Close all existing instances
    print("Closing existing ScoreBlocker instances...")
    try:
        result = subprocess.run(
            [sys.executable, score_blocker_script, '--close_all'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Error closing instances: {e}")

    time.sleep(0.5)  # Brief pause to ensure processes are closed

    # Step 2: Launch primary window
    print("Launching primary window...")
    subprocess.Popen(
        ['pythonw', score_blocker_script, '--config_file', config_file, '--position', 'primary'],
        shell=False,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    # Step 3: Launch secondary window
    print("Launching secondary window...")
    subprocess.Popen(
        ['pythonw', score_blocker_script, '--config_file', config_file, '--position', 'secondary'],
        shell=False,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    print("ScoreBlocker windows launched successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Launch ScoreBlocker 2000 with specified monitor configuration'
    )
    parser.add_argument(
        'config_file',
        help='Path to configuration file (e.g., configs/monitor1.json)'
    )

    args = parser.parse_args()
    launch_monitor_setup(args.config_file)
