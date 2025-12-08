"""
Flask WSGI application for Render health checks
"""

import logging
import os
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app for health checks
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

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    app.run(host='0.0.0.0', port=port, threaded=True)