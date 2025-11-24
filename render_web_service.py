"""
Render Web Service wrapper for HU Counseling Bot
Runs the Telegram bot in a background thread while serving a minimal HTTP endpoint
"""

import threading
import logging
import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint for Render Web Service"""
    return {
        "status": "ok",
        "service": "HU Counseling Bot",
        "bot": "running"
    }, 200

@app.route('/health')
def health():
    """Alternative health endpoint"""
    return "OK", 200

def run_bot():
    """Run the bot in this thread"""
    try:
        logger.info("Starting Telegram bot in background thread...")
        
        # Check environment variables first
        bot_token = os.getenv('BOT_TOKEN')
        admin_ids = os.getenv('ADMIN_IDS')
        
        if not bot_token:
            logger.error("❌ BOT_TOKEN not found in environment variables!")
            return
        
        if not admin_ids:
            logger.error("❌ ADMIN_IDS not found in environment variables!")
            return
            
        logger.info(f"✅ BOT_TOKEN found (length: {len(bot_token)})")
        logger.info(f"✅ ADMIN_IDS found: {admin_ids}")
        
        # Import and run bot
        logger.info("Importing bot modules...")
        from main_counseling_bot import main as bot_main
        logger.info("Bot modules imported successfully. Starting bot...")
        
        # Create and run event loop in this thread
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the bot in the event loop
        loop.run_until_complete(asyncio.gather(
            asyncio.to_thread(bot_main)
        ))
        
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        import traceback
        logger.error(f"Full error: {traceback.format_exc()}")

# Start bot thread immediately when module loads
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
logger.info("Bot thread started. Starting Flask server...")

if __name__ == '__main__':
    # Start Flask server (Render will override with gunicorn)
    app.run(host='0.0.0.0', port=5000)
