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
        # Import and run bot
        from main_counseling_bot import main as bot_main
        bot_main()
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
