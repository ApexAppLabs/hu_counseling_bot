"""
Rate Limiter for HU Counseling Service Bot
Prevents spam and abuse
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple rate limiter to prevent spam
    Tracks actions per user within time windows
    """
    
    def __init__(self):
        # user_id -> {action_type: [(timestamp, count)]}
        self.user_actions: Dict[int, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        
        # Rate limits: (max_actions, time_window_seconds)
        self.limits = {
            'message': (20, 60),           # 20 messages per minute
            'session_request': (3, 3600),   # 3 session requests per hour
            'button_click': (30, 60),       # 30 button clicks per minute
            'counselor_register': (2, 86400) # 2 registration attempts per day
        }
    
    def check_rate_limit(self, user_id: int, action_type: str) -> Tuple[bool, int]:
        """
        Check if user has exceeded rate limit for an action
        
        Args:
            user_id: Telegram user ID
            action_type: Type of action (message, session_request, etc.)
            
        Returns:
            Tuple of (is_allowed, seconds_until_reset)
            - is_allowed: True if action is allowed
            - seconds_until_reset: Seconds until rate limit resets (0 if allowed)
        """
        if action_type not in self.limits:
            logger.warning(f"Unknown action type: {action_type}")
            return True, 0
        
        max_actions, time_window = self.limits[action_type]
        current_time = time.time()
        
        # Get user's action history for this type
        actions = self.user_actions[user_id][action_type]
        
        # Remove old actions outside time window
        actions[:] = [ts for ts in actions if current_time - ts < time_window]
        
        # Check if limit exceeded
        if len(actions) >= max_actions:
            # Calculate when the oldest action will expire
            oldest_action = min(actions)
            seconds_until_reset = int(time_window - (current_time - oldest_action))
            
            logger.warning(
                f"Rate limit exceeded for user {user_id}, action: {action_type}. "
                f"Reset in {seconds_until_reset}s"
            )
            return False, seconds_until_reset
        
        # Add current action
        actions.append(current_time)
        return True, 0
    
    def reset_user(self, user_id: int, action_type: str = None):
        """
        Reset rate limit for a user
        
        Args:
            user_id: User ID to reset
            action_type: Specific action type to reset (None = reset all)
        """
        if action_type:
            if user_id in self.user_actions:
                self.user_actions[user_id][action_type] = []
        else:
            if user_id in self.user_actions:
                del self.user_actions[user_id]
        
        logger.info(f"Rate limit reset for user {user_id}, action: {action_type or 'all'}")
    
    def cleanup_old_data(self, max_age_seconds: int = 86400):
        """
        Clean up old tracking data (run periodically)
        
        Args:
            max_age_seconds: Remove data older than this (default: 24 hours)
        """
        current_time = time.time()
        users_to_remove = []
        
        for user_id, actions_dict in self.user_actions.items():
            for action_type, timestamps in list(actions_dict.items()):
                # Remove old timestamps
                timestamps[:] = [ts for ts in timestamps if current_time - ts < max_age_seconds]
                
                # Remove empty action types
                if not timestamps:
                    del actions_dict[action_type]
            
            # Mark users with no actions for removal
            if not actions_dict:
                users_to_remove.append(user_id)
        
        # Remove users with no tracked actions
        for user_id in users_to_remove:
            del self.user_actions[user_id]
        
        if users_to_remove:
            logger.info(f"Cleaned up rate limiter data for {len(users_to_remove)} users")

# Global rate limiter instance
rate_limiter = RateLimiter()

# Decorator for rate limiting
def rate_limit(action_type: str):
    """
    Decorator to add rate limiting to handler functions
    
    Usage:
        @rate_limit('message')
        async def handle_message(update, context):
            ...
    """
    def decorator(func):
        async def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            
            allowed, seconds_until_reset = rate_limiter.check_rate_limit(user_id, action_type)
            
            if not allowed:
                # User exceeded rate limit
                if update.callback_query:
                    await update.callback_query.answer(
                        f"⚠️ Too many requests. Please wait {seconds_until_reset} seconds.",
                        show_alert=True
                    )
                elif update.message:
                    await update.message.reply_text(
                        f"⚠️ You're sending messages too quickly. "
                        f"Please wait {seconds_until_reset} seconds before trying again."
                    )
                return
            
            # Rate limit passed, execute function
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    return decorator

# Example usage:
"""
from rate_limiter import rate_limit, rate_limiter

@rate_limit('message')
async def handle_session_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Your message handling code
    ...

@rate_limit('session_request')
async def request_counseling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Your session request code
    ...
"""
