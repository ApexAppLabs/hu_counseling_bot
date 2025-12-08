# 🏃 Health Ping Service for Render Deployment

## Overview

This document explains how to configure and use the internal health ping service that prevents your Render service from sleeping/idling.

## ⚠️ Important Note

**The internal scheduled tasks do NOT prevent Render service sleeping.** They run within the same process as your bot, so when the service sleeps, the scheduled tasks sleep too.

The health ping service is specifically designed to prevent sleeping.

## 🏃 How Health Ping Works

The health ping service periodically sends HTTP requests to your own service's `/health` endpoint to:
1. Keep the Render service active
2. Prevent the 1-minute cold start delay
3. Maintain continuous availability

## ⚙️ Configuration

### Environment Variables

Set these environment variables in your Render dashboard:

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `RENDER` | *(set automatically by Render)* | Must be "true" for health ping to activate |
| `HEALTH_PING_INTERVAL` | `10` | Minutes between pings (recommended: 10 minutes) |
| `HEALTH_PING_URL` | `http://localhost:5000` | URL to ping (usually auto-detected) |

### Render Dashboard Setup

1. Go to your Render service → **Environment Variables**
2. Add these variables:
   ```
   HEALTH_PING_INTERVAL=10    # Ping every 10 minutes
   ```

Note: Render automatically sets the `RENDER=true` environment variable.

## 📊 Monitoring

Check your Render logs for these entries:

```
# Successful ping
INFO:Health ping service started (interval: 600 seconds)
INFO:✅ Health ping successful at 2023-12-08 12:00:00

# Failed ping
WARNING:⚠️ Health ping timeout
ERROR:❌ Health ping failed: Connection refused
```

## 🛠️ Troubleshooting

### Service Not Staying Awake

1. Verify `RENDER=true` is set (Render does this automatically)
2. Check logs for "Health ping service started"
3. Ensure `HEALTH_PING_INTERVAL` is reasonable (5-14 minutes)

### Ping Failures

1. Check that your `/health` endpoint is working
2. Verify the service URL is correct
3. Look for network connectivity issues

### Still Getting Cold Starts

1. Ensure the health ping service is actually running
2. Check that pings are occurring regularly
3. Consider using an external ping service as backup

## 🔄 Alternative: External Ping Services

If you prefer to keep using external services, you can disable the internal health ping and use:

### Free Options:
- **UptimeRobot** - Free tier with 5-minute checks
- **Pingdom** - Free tier available
- **Better Uptime** - Free tier with basic monitoring

### Setup:
Point the service to your health endpoint:
```
GET https://your-app.onrender.com/health
```

## 📈 Performance Impact

The health ping service is lightweight:
- Minimal bandwidth usage (~100 bytes per ping)
- Negligible CPU impact
- Single persistent HTTP connection
- Automatic retry on failures

## 🆘 Support

If you encounter issues:

1. Check Render logs for health ping messages
2. Verify your `/health` endpoint works manually
3. Ensure environment variables are set correctly
4. Test with external ping service as comparison

For assistance, refer to:
- `health_ping.py` - Core implementation
- This document for configuration guidance