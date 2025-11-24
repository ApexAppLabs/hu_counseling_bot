"""
Render Web Service wrapper for HU Counseling Bot
Runs the Telegram bot in a background thread while serving a minimal HTTP endpoint
"""

import threading
import logging
from flask import Flask
from main_counseling_bot import main as bot_main

# Configure logging
logging.basicConfig(level=logging.INFO)
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
        bot_main()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Bot thread started. Starting Flask server...")

    # Start Flask server (Render will override with gunicorn)
    app.run(host='0.0.0.0', port=5000)
