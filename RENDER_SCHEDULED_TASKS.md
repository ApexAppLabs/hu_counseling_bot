# 🕐 Internal Scheduled Tasks for Render Deployment

## Overview

This document explains how to configure and manage internal scheduled tasks for your HU Counseling Bot when deployed on Render. These tasks replace external cron jobs with internal background processes that run continuously within your application.

## 🔄 Internal Scheduled Tasks

The following tasks now run automatically within your bot:

1. **Database Backup** - Automatic database backups (default: every 24 hours)
2. **Session Cleanup** - Removes old ended sessions and messages (default: every 30 minutes)
3. **Pending Session Auto-Match** - Automatically matches pending sessions with available counselors (default: every 5 minutes)

## ⚙️ Configuration

### Environment Variables

You can customize the frequency of scheduled tasks using these environment variables in your Render dashboard:

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `BACKUP_INTERVAL_MINUTES` | `1440` (24 hours) | How often to backup the database |
| `CLEANUP_INTERVAL_MINUTES` | `30` | How often to clean up old sessions |
| `MATCH_INTERVAL_MINUTES` | `5` | How often to auto-match pending sessions |

### Setting Up in Render Dashboard

1. Go to your Render service → **Environment Variables**
2. Add any of the variables above to customize intervals
3. Example:
   ```
   BACKUP_INTERVAL_MINUTES=720    # Backup every 12 hours instead of 24
   CLEANUP_INTERVAL_MINUTES=60    # Clean up every hour instead of 30 minutes
   ```

## ▶️ Manual Trigger

You can manually run scheduled tasks using the command line:

```bash
# Run specific task
python run_scheduled_tasks.py backup    # Manual database backup
python run_scheduled_tasks.py cleanup   # Manual session cleanup
python run_scheduled_tasks.py match     # Manual auto-matching
python run_scheduled_tasks.py all       # Run all tasks
```

## 📊 Monitoring

Check your Render logs to monitor scheduled task execution:

```
# Look for these log entries:
INFO:Scheduled tasks manager started
INFO:Database backed up to: backups/hu_counseling_backup_20231208_120000.db
INFO:Cleaned up 0 old sessions and 0 messages
INFO:Auto-matched 2 pending sessions
```

## 🛠️ Troubleshooting

### Tasks Not Running

1. Check that your Render service is using the updated code
2. Verify logs show "Scheduled tasks manager started"
3. Ensure sufficient resources (tasks run in background)

### Database Backup Failures

1. Check file permissions for the `backups/` directory
2. Verify disk space is available
3. Ensure the backup directory exists and is writable

### Auto-Match Not Working

1. Verify counselors have correct specializations
2. Check that counselors are approved and available
3. Review matching system logs for specific errors

## 📈 Performance Impact

The scheduled tasks are designed to be lightweight:
- Minimal CPU usage during sleep intervals
- Low memory footprint
- Non-blocking execution using asyncio
- Automatic retry on failures

## 🔄 Migration from External Cron

If you were using external cron jobs:

1. Remove external cron job configuration
2. Deploy the updated code to Render
3. Verify internal tasks are running via logs
4. Test functionality (manual trigger if needed)

## 🆘 Support

If you encounter issues:

1. Check Render logs for error messages
2. Run manual trigger to test specific tasks
3. Verify environment variables are set correctly
4. Ensure your Render service has adequate resources

For assistance, refer to:
- `scheduled_tasks.py` - Core implementation
- `run_scheduled_tasks.py` - Manual trigger script
- This document for configuration guidance