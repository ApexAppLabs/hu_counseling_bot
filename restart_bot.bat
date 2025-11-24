@echo off
echo.
echo ========================================
echo   Restarting Bot with Fresh Database
echo ========================================
echo.

REM Stop any running Python processes
echo [1/3] Stopping old bot instances...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

REM Delete old database
echo [2/3] Deleting old database...
if exist confession_bot.db (
    del /F confession_bot.db
    echo    - Old database deleted
) else (
    echo    - No old database found
)
echo.

REM Start bot
echo [3/3] Starting bot with new database...
echo.
echo ========================================
echo   Bot Starting...
echo   Press Ctrl+C to stop
echo ========================================
echo.

python bot_professional.py

pause
