#!/usr/bin/env python3
"""
Manual trigger for scheduled tasks
Can be used for testing or manual execution
"""

import asyncio
import logging
from counseling_database import CounselingDatabase
from scheduled_tasks import ScheduledTasksManager
from matching_system import CounselingMatcher

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_manual_backup():
    """Manually trigger database backup"""
    logger.info("Running manual database backup...")
    db = CounselingDatabase()
    
    from backup_database import backup_database
    backup_path = backup_database(db.db_path)
    if backup_path:
        logger.info(f"✅ Database backed up to: {backup_path}")
    else:
        logger.error("❌ Database backup failed")

async def run_manual_session_cleanup():
    """Manually trigger session cleanup"""
    logger.info("Running manual session cleanup...")
    db = CounselingDatabase()
    
    # Clean up old ended sessions (older than 30 days)
    from datetime import datetime, timedelta
    conn = db.get_connection()
    cursor = conn.cursor()
    ph = db.param_placeholder
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    cursor.execute(f'''
        DELETE FROM session_messages 
        WHERE session_id IN (
            SELECT session_id FROM counseling_sessions 
            WHERE status = 'ended' AND ended_at < {ph}
        )
    ''', (thirty_days_ago.isoformat(),))
    
    deleted_messages = cursor.rowcount
    
    cursor.execute(f'''
        DELETE FROM counseling_sessions 
        WHERE status = 'ended' AND ended_at < {ph}
    ''', (thirty_days_ago.isoformat(),))
    
    deleted_sessions = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Cleaned up {deleted_sessions} old sessions and {deleted_messages} messages")

async def run_manual_auto_match():
    """Manually trigger auto-matching of pending sessions"""
    logger.info("Running manual auto-matching of pending sessions...")
    db = CounselingDatabase()
    matcher = CounselingMatcher(db)
    
    # Auto-match pending sessions
    matched_pairs = matcher.auto_match_pending_sessions()
    
    if matched_pairs:
        logger.info(f"✅ Auto-matched {len(matched_pairs)} pending sessions")
        for session_id, counselor_id in matched_pairs:
            logger.info(f"  Session {session_id} -> Counselor {counselor_id}")
    else:
        logger.info("ℹ️ No pending sessions to match")

async def run_all_tasks():
    """Run all scheduled tasks manually"""
    logger.info("Running all scheduled tasks...")
    
    await run_manual_backup()
    await run_manual_session_cleanup()
    await run_manual_auto_match()
    
    logger.info("✅ All scheduled tasks completed")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        task = sys.argv[1].lower()
        if task == "backup":
            asyncio.run(run_manual_backup())
        elif task == "cleanup":
            asyncio.run(run_manual_session_cleanup())
        elif task == "match":
            asyncio.run(run_manual_auto_match())
        elif task == "all":
            asyncio.run(run_all_tasks())
        else:
            print(f"Usage: python run_scheduled_tasks.py [backup|cleanup|match|all]")
    else:
        print(f"Usage: python run_scheduled_tasks.py [backup|cleanup|match|all]")