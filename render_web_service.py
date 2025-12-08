"""
Render Web Service wrapper for HU Counseling Bot
Runs the Telegram bot in a background thread while serving a minimal HTTP endpoint
"""

import threading
import logging
import os
import signal
import sys
from flask import Flask
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global reference to bot application
bot_app = None

@app.route('/')
def health_check():
    """Health check endpoint for Render Web Service"""
    return {
        "status": "ok",
        "service": "HU Counseling Bot",
        "bot": "running" if bot_app else "starting"
    }, 200

@app.route('/health')
def health():
    """Alternative health endpoint"""
    return "OK", 200

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    if bot_app:
        logger.info("Stopping bot application...")
        # Note: In a real implementation, we would properly shut down the bot
        # For now, we'll just log that shutdown was requested
    sys.exit(0)

def run_bot():
    """Run the bot in this thread"""
    global bot_app
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
        
        # Import and initialize bot
        logger.info("Importing bot modules...")
        from main_counseling_bot import initialize_bot
        logger.info("Bot modules imported successfully. Initializing bot...")
        
        # Initialize the bot application
        bot_app = initialize_bot()
        if bot_app is None:
            logger.error("Failed to initialize bot application")
            return
            
        logger.info("Bot initialized successfully. Starting bot in polling mode...")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Run the bot in polling mode in this thread
        import asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())
        bot_app.run_polling(stop_signals=None)
        
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
    port = int(os.getenv("PORT", "5000"))
    app.run(host='0.0.0.0', port=port)