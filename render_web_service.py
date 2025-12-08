"""
Render Web Service wrapper for HU Counseling Bot
Runs the Telegram bot as the main application with Flask in a background thread
"""

import threading
import logging
import os
import asyncio
from flask import Flask
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global reference to Flask app
flask_app = None

def create_flask_app():
    """Create Flask app for health checks"""
    app = Flask(__name__)

    @app.route('/')
    def health_check():
        """Health check endpoint for Render Web Service"""
        return {
            "status": "ok",
            "service": "HU Counseling Bot",
            "flask": "running"
        }, 200

    @app.route('/health')
    def health():
        """Alternative health endpoint"""
        return "OK", 200
        
    return app

def run_flask():
    """Run Flask app in a separate thread"""
    global flask_app
    try:
        flask_app = create_flask_app()
        port = int(os.getenv("PORT", "5000"))
        logger.info(f"Starting Flask server on port {port}")
        flask_app.run(host='0.0.0.0', port=port, threaded=True)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def main():
    """Main entry point - run bot as primary service with Flask as secondary"""
    logger.info("Starting HU Counseling Bot service...")
    
    # Start Flask in background thread for health checks
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started in background thread")
    
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
        
    logger.info("Bot initialized successfully. Starting bot...")
    
    # Check if we should use webhook mode (Render deployment)
    use_webhook = os.getenv("USE_WEBHOOK", "true").lower() == "true"
    
    if use_webhook:
        # Webhook configuration for Render deployment
        base_url = os.getenv("WEBHOOK_BASE_URL")
        port = int(os.getenv("PORT", "5000"))
        url_path = os.getenv("WEBHOOK_PATH", "telegram-webhook")
        
        if not base_url:
            logger.error("❌ WEBHOOK_BASE_URL not set but USE_WEBHOOK=true. Cannot start bot!")
            return
        
        base_url = base_url.rstrip("/")
        webhook_url = f"{base_url}/{url_path}"
        
        logger.info("🌐 Starting in WEBHOOK mode")
        logger.info(f"🔗 Webhook URL: {webhook_url}")
        logger.info(f"🔌 Listening on 0.0.0.0:{port}, url_path='{url_path}'")
        
        # Run webhook in main thread (this is correct)
        bot_app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=url_path,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        # Polling mode (for local development)
        logger.info("📡 Starting in POLLING mode")
        bot_app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()