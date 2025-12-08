import os
import shutil
import logging
from datetime import datetime
from counseling_database import USE_POSTGRES

logger = logging.getLogger(__name__)

def backup_database(db_path: str):
    """Backup database - handles both SQLite and PostgreSQL"""
    try:
        # Check if using PostgreSQL
        if USE_POSTGRES:
            logger.info("⏭️ Skipping SQLite backup - using PostgreSQL backend")
            return True
        
        # Original SQLite backup logic
        if not os.path.exists(db_path):
            logger.warning(f"Database file {db_path} not found")
            return False
            
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{db_path}.backup_{timestamp}"
        
        # Copy database file
        shutil.copy2(db_path, backup_filename)
        logger.info(f"✅ Database backed up to {backup_filename}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return False