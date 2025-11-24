@echo off
echo ================================================
echo   Confession Bot - Quick Deployment Script
echo ================================================
echo.

echo [1/4] Adding all changes...
git add .

echo.
echo [2/4] Committing changes...
git commit -m "Fix: Update health check path and add diagnostic tools"

echo.
echo [3/4] Pushing to GitHub...
git push origin main

echo.
echo [4/4] Deployment initiated!
echo.
echo ================================================
echo   Next Steps:
echo ================================================
echo.
echo 1. Wait 2-3 minutes for Koyeb to redeploy
echo 2. Run: python test_bot_webhook.py
echo 3. Test bot by sending /start to @haru_confessions_bot
echo.
echo ================================================
pause
