"""Database backup utility for HU Counseling Service Bot"""
import shutil
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def backup_database(db_path='hu_counseling.db', backup_dir='backups'):
    """Create a timestamped backup of the database"""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'hu_counseling_backup_{timestamp}.db')
    
    try:
        shutil.copy2(db_path, backup_file)
        logger.info(f"✅ Database backed up to: {backup_file}")
        
        # Keep only last 7 backups
        cleanup_old_backups(backup_dir, keep=7)
        return backup_file
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return None

def cleanup_old_backups(backup_dir, keep=7):
    """Keep only the most recent backups"""
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
    if len(backups) > keep:
        for old_backup in backups[:-keep]:
            os.remove(os.path.join(backup_dir, old_backup))
            logger.info(f"Removed old backup: {old_backup}")

if __name__ == '__main__':
    backup_database()
