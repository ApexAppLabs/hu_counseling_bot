# 🚀 Deploy to Render (Web Service) - Quick Guide

## Why Web Service?

- You chose Render's **Web Service** option
- Web Services require an HTTP server and port binding
- This wrapper runs your Telegram bot (polling) in a background thread while serving a minimal HTTP endpoint

---

## 📋 Prerequisites

1. ✅ **Telegram Bot Token** from @BotFather
2. ✅ **Your Telegram User ID** from @userinfobot
3. ✅ **Code pushed to GitHub**

---

## 🚀 Step 1: Push to GitHub (if not already)

```bash
git add .
git commit -m "Add Render Web Service wrapper"
git push origin main
```

---

## 🚀 Step 2: Create Render Web Service

1. Go to **Render Dashboard**
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Select branch: `main`

---

## ⚙️ Step 3: Configure Web Service

### Build & Start Commands

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn render_web_service:app`

### Environment Variables

Add these in the Render dashboard:

| Name | Value |
|------|-------|
| `BOT_TOKEN` | Your bot token from @BotFather |
| `ADMIN_IDS` | Your user ID (comma-separated, no spaces) |

**Example ADMIN_IDS**: `123456789` or `123456789,987654321`

---

## 🚀 Step 4: Deploy

1. Click **Create Web Service** / **Deploy**
2. Wait for build (2-3 minutes)
3. Open **Logs** tab

**Expected logs:**
```
Starting Telegram bot in background thread...
Bot thread started. Starting Flask server...
🚀 HU Counseling Service Bot is starting...
✅ Ready to serve!
```

---

## 🧪 Step 5: Test

1. Open your bot in Telegram
2. Send `/start`
3. Bot should respond normally

**Health check:** Visit `https://your-app.onrender.com/health` — should return `OK`

---

## 📱 Auto-Deploy (Optional)

- In Render service → **Settings**
- Enable **Auto-Deploy** for your branch
- Now every `git push` auto-redeploys

---

## 🛟 Troubleshooting

### Build fails
- Check `requirements.txt` includes `flask` and `gunicorn`
- Verify Python version in `runtime.txt` (3.11.9)

### Bot doesn't respond
- Check logs for bot startup messages
- Verify `BOT_TOKEN` and `ADMIN_IDS` env vars
- Ensure service type is **Web Service** (not Worker)

### Health check fails
- Ensure `render_web_service.py` is committed
- Verify Procfile: `web: gunicorn render_web_service:app`

---

## ✅ Success!

Your bot is now:
- ✅ Running on Render Web Service
- ✅ Polling in background thread
- ✅ Serving HTTP endpoint for health checks
- ✅ Ready 24/7

Share your bot link: `https://t.me/YOUR_BOT_USERNAME`
