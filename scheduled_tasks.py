"""
Scheduled Tasks Manager for HU Counseling Bot
Handles recurring tasks like database backups, session cleanup, etc.
"""

import asyncio
import logging
from datetime import datetime, timedelta
import os
from backup_database import backup_database
from counseling_database import CounselingDatabase
from matching_system import CounselingMatcher

logger = logging.getLogger(__name__)

class ScheduledTasksManager:
    """
    Manages all scheduled/background tasks for the bot
    Runs continuously in the background
    """
    
    def __init__(self, db: CounselingDatabase):
        self.db = db
        self.is_running = False
        self.tasks = []
        
    async def start(self):
        """Start all scheduled tasks"""
        self.is_running = True
        logger.info("Scheduled tasks manager started")
        
        # Start all background tasks
        self.tasks = [
            asyncio.create_task(self.database_backup_task()),
            asyncio.create_task(self.session_cleanup_task()),
            asyncio.create_task(self.pending_session_auto_match_task()),
        ]
        
        # Wait for all tasks (they should run indefinitely)
        try:
            await asyncio.gather(*self.tasks)
        except Exception as e:
            logger.error(f"Error in scheduled tasks: {e}")
    
    async def stop(self):
        """Stop all scheduled tasks"""
        self.is_running = False
        logger.info("Scheduled tasks manager stopping")
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete cancellation
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("Scheduled tasks manager stopped")
    
    async def database_backup_task(self):
        """Periodically backup the database"""
        backup_interval = int(os.getenv("BACKUP_INTERVAL_MINUTES", "1440"))  # Default: 24 hours
        logger.info(f"Database backup task started (interval: {backup_interval} minutes)")
        
        while self.is_running:
            try:
                # Perform backup
                backup_path = backup_database(self.db.db_path)
                if backup_path:
                    logger.info(f"Database backed up to: {backup_path}")
                else:
                    logger.warning("Database backup failed")
                    
                # Wait for next interval
                await asyncio.sleep(backup_interval * 60)  # Convert minutes to seconds
                
            except asyncio.CancelledError:
                logger.info("Database backup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in database backup task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def session_cleanup_task(self):
        """Clean up expired/inactive sessions"""
        cleanup_interval = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "30"))  # Default: 30 minutes
        logger.info(f"Session cleanup task started (interval: {cleanup_interval} minutes)")
        
        while self.is_running:
            try:
                # Clean up old ended sessions (older than 30 days)
                conn = self.db.get_connection()
                cursor = conn.cursor()
                ph = self.db.param_placeholder
                
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
                
                if deleted_sessions > 0 or deleted_messages > 0:
                    logger.info(f"Cleaned up {deleted_sessions} old sessions and {deleted_messages} messages")
                
                # Wait for next interval
                await asyncio.sleep(cleanup_interval * 60)  # Convert minutes to seconds
                
            except asyncio.CancelledError:
                logger.info("Session cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in session cleanup task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def pending_session_auto_match_task(self):
        """Automatically match pending sessions with available counselors"""
        match_interval = int(os.getenv("MATCH_INTERVAL_MINUTES", "5"))  # Default: 5 minutes
        logger.info(f"Pending session auto-match task started (interval: {match_interval} minutes)")
        
        matcher = CounselingMatcher(self.db)
        
        while self.is_running:
            try:
                # Auto-match pending sessions
                matched_pairs = matcher.auto_match_pending_sessions()
                
                if matched_pairs:
                    logger.info(f"Auto-matched {len(matched_pairs)} pending sessions")
                    for session_id, counselor_id in matched_pairs:
                        logger.info(f"  Session {session_id} -> Counselor {counselor_id}")
                        
                        # Notify counselor of new match
                        try:
                            session = self.db.get_session(session_id)
                            counselor = self.db.get_counselor(counselor_id)
                            
                            if session and counselor:
                                from telegram import Bot
                                
                                bot_token = os.getenv('BOT_TOKEN')
                                if bot_token:
                                    bot = Bot(token=bot_token)
                                    
                                    # Get session details
                                    from counseling_database import COUNSELING_TOPICS
                                    topic_data = COUNSELING_TOPICS.get(session['topic'], {})
                                    
                                    # Send notification to counselor
                                    keyboard = [[
                                        {"text": "✅ Accept Session", "callback_data": f"accept_session_{session_id}"},
                                        {"text": "❌ Decline", "callback_data": f"decline_session_{session_id}"}
                                    ]]
                                    
                                    await bot.send_message(
                                        chat_id=counselor['user_id'],
                                        text=f"**🔔 New Counseling Request**\n\n"
                                             f"**Topic:** {topic_data.get('icon', '💬')} {topic_data.get('name', session['topic'])}\n"
                                             f"**Description:** {session.get('description', 'No description provided')[:100]}{'...' if len(session.get('description', '')) > 100 else ''}\n\n"
                                             f"Would you like to accept this session?",
                                        reply_markup={"inline_keyboard": keyboard},
                                        parse_mode='Markdown'
                                    )
                        except Exception as notify_error:
                            logger.error(f"Failed to notify counselor {counselor_id} about session {session_id}: {notify_error}")
                
                # Wait for next interval
                await asyncio.sleep(match_interval * 60)  # Convert minutes to seconds
                
            except asyncio.CancelledError:
                logger.info("Pending session auto-match task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in pending session auto-match task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

# Integration example
"""
To integrate this with your bot, add this to the post_init function in main_counseling_bot.py:

async def post_init(application):
    
    # Start scheduled tasks manager
    from scheduled_tasks import ScheduledTasksManager
    scheduled_tasks_manager = ScheduledTasksManager(db)
    application.bot_data['scheduled_tasks_manager'] = scheduled_tasks_manager
    asyncio.create_task(scheduled_tasks_manager.start())
    logger.info("✅ Scheduled tasks manager started")
    

And add this to the shutdown handler:

async def post_shutdown(application):
    # Stop scheduled tasks manager
    if 'scheduled_tasks_manager' in application.bot_data:
        await application.bot_data['scheduled_tasks_manager'].stop()
"""