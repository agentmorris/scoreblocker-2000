@echo off
python score_blocker.py --close_all > output.txt 2>&1
echo Exit code: %ERRORLEVEL% >> output.txt
type output.txt
