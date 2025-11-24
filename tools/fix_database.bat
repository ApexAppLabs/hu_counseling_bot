@echo off
echo.
echo ============================================
echo   Fixing Database - Adding Display Name
echo ============================================
echo.

REM Stop any running Python processes
echo [1/3] Stopping bot...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul
echo    - Bot stopped

REM Delete old database
echo.
echo [2/3] Deleting old database...
if exist confession_bot.db (
    del /F confession_bot.db
    echo    - Old database deleted
    echo    - New database will be created with display_name column
) else (
    echo    - No old database found
)
echo.

REM Start bot
echo [3/3] Starting bot with new database schema...
echo.
echo ============================================
echo   Bot Starting...
echo   Press Ctrl+C to stop
echo ============================================
echo.

python bot_professional.py

pause
