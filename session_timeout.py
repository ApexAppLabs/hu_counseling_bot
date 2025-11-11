"""
Session Timeout Manager
Automatically ends stale sessions after inactivity
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

class SessionTimeoutManager:
    """
    Manages automatic session timeouts
    Runs in background to check for inactive sessions
    """
    
    def __init__(self, db, bot_context, timeout_hours: int = 24):
        """
        Initialize timeout manager
        
        Args:
            db: Database instance
            bot_context: Bot application context for sending messages
            timeout_hours: Hours of inactivity before auto-ending (default: 24)
        """
        self.db = db
        self.bot_context = bot_context
        self.timeout_hours = timeout_hours
        self.is_running = False
        self.check_interval = 300  # Check every 5 minutes
    
    async def start(self):
        """Start the timeout checker loop"""
        self.is_running = True
        logger.info(f"Session timeout manager started (timeout: {self.timeout_hours} hours)")
        
        while self.is_running:
            try:
                await self.check_and_timeout_sessions()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in timeout manager: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop(self):
        """Stop the timeout checker loop"""
        self.is_running = False
        logger.info("Session timeout manager stopped")
    
    async def check_and_timeout_sessions(self):
        """
        Check for inactive sessions and auto-end them
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get all active and matched sessions
            cursor.execute('''
                SELECT session_id, user_id, counselor_id, topic, started_at, matched_at
                FROM counseling_sessions
                WHERE status IN ('active', 'matched')
            ''')
            
            sessions = cursor.fetchall()
            timeout_threshold = datetime.now() - timedelta(hours=self.timeout_hours)
            timed_out_count = 0
            
            for session in sessions:
                session_id = session['session_id']
                
                # Get last message time
                cursor.execute('''
                    SELECT MAX(created_at) as last_message
                    FROM session_messages
                    WHERE session_id = ?
                ''', (session_id,))
                
                result = cursor.fetchone()
                last_message_str = result['last_message'] if result else None
                
                # Determine the reference time
                if last_message_str:
                    # Use last message time
                    last_activity = datetime.fromisoformat(last_message_str)
                elif session['started_at']:
                    # Use session start time if no messages
                    last_activity = datetime.fromisoformat(session['started_at'])
                elif session['matched_at']:
                    # Use match time if not started
                    last_activity = datetime.fromisoformat(session['matched_at'])
                else:
                    # Skip if no time reference
                    continue
                
                # Check if session has timed out
                if last_activity < timeout_threshold:
                    await self.timeout_session(session)
                    timed_out_count += 1
            
            if timed_out_count > 0:
                logger.info(f"Timed out {timed_out_count} inactive sessions")
                
        except Exception as e:
            logger.error(f"Error checking session timeouts: {e}")
        finally:
            conn.close()
    
    async def timeout_session(self, session):
        """
        End a session due to timeout and notify parties
        
        Args:
            session: Session record from database
        """
        session_id = session['session_id']
        user_id = session['user_id']
        counselor_id = session['counselor_id']
        
        try:
            # End the session in database
            self.db.end_session(session_id, 'timeout')
            
            # Notify user
            try:
                await self.bot_context.bot.send_message(
                    chat_id=user_id,
                    text="⏰ **Session Timeout**\n\n"
                         f"Your counseling session has been automatically ended due to {self.timeout_hours} hours of inactivity.\n\n"
                         "If you still need support, feel free to request a new session anytime. 🙏",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Could not notify user {user_id} of timeout: {e}")
            
            # Notify counselor if session was active
            if counselor_id and session['started_at']:
                try:
                    counselor = self.db.get_counselor(counselor_id)
                    if counselor:
                        await self.bot_context.bot.send_message(
                            chat_id=counselor['user_id'],
                            text="⏰ **Session Timeout**\n\n"
                                 f"Your counseling session (ID: #{session_id}) has been automatically ended due to inactivity.\n\n"
                                 "No action needed from you.",
                            parse_mode='Markdown'
                        )
                except Exception as e:
                    logger.warning(f"Could not notify counselor {counselor_id} of timeout: {e}")
            
            logger.info(f"Session {session_id} timed out and ended")
            
        except Exception as e:
            logger.error(f"Error timing out session {session_id}: {e}")

# Example integration in main bot:
"""
from session_timeout import SessionTimeoutManager

async def post_init(application):
    # Start timeout manager
    timeout_manager = SessionTimeoutManager(
        db=db, 
        bot_context=application,
        timeout_hours=24
    )
    
    # Store in application context for later access
    application.bot_data['timeout_manager'] = timeout_manager
    
    # Start the background task
    asyncio.create_task(timeout_manager.start())
    
    logger.info("✅ Session timeout manager started")

async def post_shutdown(application):
    # Stop timeout manager on shutdown
    if 'timeout_manager' in application.bot_data:
        await application.bot_data['timeout_manager'].stop()
"""
