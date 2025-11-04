#!/usr/bin/env python3
"""Direct test of close_all_instances function"""

import subprocess
import os

def close_all_instances():
    """Close all running ScoreBlocker instances"""
    killed_count = 0

    try:
        print("Starting close_all_instances...")

        # Use PowerShell with WMI to find processes by command line
        ps_script = """
        Get-WmiObject Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" |
        Where-Object { $_.CommandLine -like '*score_blocker.py*' } |
        ForEach-Object { $_.ProcessId }
        """

        print("Running PowerShell command...")
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_script],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        print(f"PowerShell return code: {result.returncode}")
        print(f"PowerShell stdout: '{result.stdout}'")
        print(f"PowerShell stderr: '{result.stderr}'")

        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"Found PIDs: {pids}")

            for pid in pids:
                pid = pid.strip()
                if pid.isdigit():
                    try:
                        print(f"Attempting to kill PID: {pid}")
                        kill_result = subprocess.run(
                            ['taskkill', '/F', '/PID', pid],
                            capture_output=True,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                        )
                        if kill_result.returncode == 0:
                            print(f"Closed ScoreBlocker instance (PID: {pid})")
                            killed_count += 1
                        else:
                            print(f"Failed to close PID {pid}: {kill_result.stderr}")
                    except Exception as e:
                        print(f"Error killing process {pid}: {e}")

        if killed_count > 0:
            print(f"Total instances closed: {killed_count}")
        else:
            print("No running ScoreBlocker instances found")

    except Exception as e:
        print(f"Error closing instances: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    close_all_instances()
