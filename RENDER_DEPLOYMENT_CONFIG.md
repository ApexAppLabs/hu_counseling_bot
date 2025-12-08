# 🚀 Render Deployment Configuration

## Overview

This document explains how to properly configure your HU Counseling Bot for deployment on Render.

## Required Environment Variables

Set these environment variables in your Render dashboard:

| Variable Name | Required | Default Value | Description |
|---------------|----------|---------------|-------------|
| `BOT_TOKEN` | ✅ Yes | None | Your Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | ✅ Yes | None | Comma-separated list of Telegram user IDs for admin access |
| `DATABASE_URL` | ✅ Yes | None | PostgreSQL connection string (from Neon or other provider) |
| `WEBHOOK_BASE_URL` | ✅ Yes | None | Your Render service URL (e.g., `https://your-app.onrender.com`) |
| `USE_WEBHOOK` | ✅ Yes | `true` | Must be "true" for Render deployment |
| `WEBHOOK_PATH` | Optional | BOT_TOKEN | Custom webhook path (defaults to bot token) |
| `PORT` | Optional | `5000` | Port for webhook listener (Render sets automatically) |

## Setting Environment Variables in Render Dashboard

1. Go to your Render service → **Environment Variables**
2. Add these required variables:

```
BOT_TOKEN=your_actual_bot_token_here
ADMIN_IDS=123456789,987654321
DATABASE_URL=your_neon_postgresql_connection_string
WEBHOOK_BASE_URL=https://your-service-name.onrender.com
USE_WEBHOOK=true
```

### Example Configuration:
```
BOT_TOKEN=1234567890:AAH1234567890abcdefghijklmnopqrstuvwxyz
ADMIN_IDS=8352539365
DATABASE_URL=postgresql://username:password@host:port/database
WEBHOOK_BASE_URL=https://hu-counseling-bot.onrender.com
USE_WEBHOOK=true
```

## Webhook Configuration Details

### WEBHOOK_BASE_URL
This is crucial for proper webhook functionality. It should be:
- Your Render service URL
- Must be publicly accessible
- Must match your deployment domain

Example: `https://hu-counseling-bot.onrender.com`

### WEBHOOK_PATH
Optional custom path for webhooks. If not set, defaults to your BOT_TOKEN.

### PORT
Render automatically sets this. Do not manually configure unless you have specific requirements.

## Health Check Configuration

Render will automatically check your service health. The application includes:
- `/` endpoint for basic health check
- `/health` endpoint for alternative health check

Both return success responses when the service is running.

## Troubleshooting

### Bot Not Responding
1. Verify `BOT_TOKEN` is correct
2. Ensure `WEBHOOK_BASE_URL` matches your Render URL
3. Check that `USE_WEBHOOK=true` is set
4. Verify `DATABASE_URL` is properly configured

### Webhook Registration Issues
1. Check Render logs for webhook setup messages
2. Verify `WEBHOOK_BASE_URL` is accessible
3. Ensure no trailing slashes in the URL

### Database Connection Problems
1. Verify `DATABASE_URL` format
2. Check Neon dashboard for connection details
3. Ensure database credentials are correct

## Local Development vs Production

| Feature | Local Development | Render Deployment |
|---------|------------------|-------------------|
| Mode | Polling | Webhook |
| `USE_WEBHOOK` | `false` or unset | `true` |
| `WEBHOOK_BASE_URL` | Not required | Required |
| `PORT` | Customizable | Set by Render |

## Example Render Logs

Successful deployment should show:
```
✅ BOT_TOKEN found (length: 46)
✅ ADMIN_IDS found: 123456789
🌐 Starting in WEBHOOK mode
🔗 Webhook URL: https://your-app.onrender.com/your_bot_token
```

## Support

If you encounter issues:
1. Check Render logs for error messages
2. Verify all required environment variables are set
3. Ensure your Telegram bot token is correct
4. Confirm database connection string is valid

For assistance, refer to:
- This document for configuration guidance
- `render_web_service.py` for webhook implementation
- `main_counseling_bot.py` for bot initialization