@echo off
echo Waiting for Koyeb to route traffic...
timeout /t 60 /nobreak
echo.
echo Testing endpoints...
python check_koyeb_config.py
echo.
echo Testing webhook...
python check_webhook.py
pause
