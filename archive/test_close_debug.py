import subprocess
import sys

try:
    result = subprocess.run(
        [sys.executable, 'score_blocker.py', '--close_all'],
        capture_output=True,
        text=True,
        timeout=10
    )
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
except Exception as e:
    print(f"Exception: {e}")
