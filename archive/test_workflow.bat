@echo off
echo ===== Testing close_all workflow =====
echo.
echo Step 1: Launching two test instances...
start /min pythonw score_blocker.py --config_file configs/monitor1.json --position primary
start /min pythonw score_blocker.py --config_file configs/monitor1.json --position secondary
timeout /t 2 /nobreak > nul

echo.
echo Step 2: Running close_all...
python score_blocker.py --close_all
set CLOSE_EXIT_CODE=%ERRORLEVEL%

echo.
echo Close command exit code: %CLOSE_EXIT_CODE%
echo.

if %CLOSE_EXIT_CODE% == 0 (
    echo SUCCESS: Close command completed successfully
) else (
    echo ERROR: Close command returned error code %CLOSE_EXIT_CODE%
)

echo.
echo Press any key to exit...
pause > nul
