"""
Logging Configuration for HU Counseling Service Bot
Configures file-based logging with rotation
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_dir='logs'):
    """
    Setup comprehensive logging for the bot
    
    Args:
        log_level: Logging level (default: INFO)
        log_dir: Directory for log files (default: 'logs')
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate log filename with date
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'counseling_bot_{today}.log')
    error_log_file = os.path.join(log_dir, f'counseling_bot_errors_{today}.log')
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler - All logs
    # Max 10MB per file, keep 5 backup files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # File Handler - Errors only
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Reduce verbosity of some libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info("=" * 60)
    root_logger.info("HU Counseling Service Bot - Logging Initialized")
    root_logger.info(f"Log directory: {os.path.abspath(log_dir)}")
    root_logger.info(f"Log level: {logging.getLevelName(log_level)}")
    root_logger.info("=" * 60)
    
    return root_logger

def get_logger(name):
    """
    Get a logger for a specific module
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

# Example usage in main bot file:
"""
from logging_config import setup_logging

# At the start of main_counseling_bot.py, replace the basic logging setup with:
setup_logging(log_level=logging.INFO)
logger = logging.getLogger(__name__)
"""
