"""
Enhanced Database module for HU Counseling Service Bot
Supports anonymous counseling sessions between users and counselors
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_locked(max_retries=3, delay=0.5):
    """Decorator to retry database operations if locked"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    if 'locked' in str(e).lower() and attempt < max_retries - 1:
                        logger.warning(f"Database locked, retrying {func.__name__} (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        raise
            return func(*args, **kwargs)  # Final attempt
        return wrapper
    return decorator

# Counseling topics for student gospel fellowship
COUNSELING_TOPICS = {
    'spiritual': {
        'name': 'Spiritual Growth & Faith',
        'icon': '🙏',
        'description': 'Questions about faith, prayer, Bible study, spiritual struggles',
        'keywords': ['faith', 'prayer', 'bible', 'god', 'jesus', 'spiritual', 'worship']
    },
    'mental_health': {
        'name': 'Mental Health & Wellness',
        'icon': '🧠',
        'description': 'Anxiety, depression, stress, emotional struggles',
        'keywords': ['anxiety', 'depression', 'stress', 'mental', 'emotional', 'overwhelmed']
    },
    'relationships': {
        'name': 'Relationships & Dating',
        'icon': '💑',
        'description': 'Dating, friendships, family issues, relationship advice',
        'keywords': ['relationship', 'dating', 'marriage', 'boyfriend', 'girlfriend', 'friend']
    },
    'academic': {
        'name': 'Academic Struggles',
        'icon': '📚',
        'description': 'Study stress, exam anxiety, time management, academic pressure',
        'keywords': ['study', 'exam', 'academic', 'school', 'university', 'grades']
    },
    'identity': {
        'name': 'Identity & Purpose',
        'icon': '🎯',
        'description': 'Life purpose, calling, identity questions, self-worth',
        'keywords': ['purpose', 'calling', 'identity', 'worth', 'meaning', 'direction']
    },
    'addiction': {
        'name': 'Addiction & Habits',
        'icon': '🚫',
        'description': 'Struggling with addictions, bad habits, temptations',
        'keywords': ['addiction', 'habit', 'temptation', 'porn', 'alcohol', 'smoking']
    },
    'grief': {
        'name': 'Grief & Loss',
        'icon': '💔',
        'description': 'Dealing with loss, grief, mourning, trauma',
        'keywords': ['grief', 'loss', 'death', 'mourning', 'trauma', 'sad']
    },
    'financial': {
        'name': 'Financial Concerns',
        'icon': '💰',
        'description': 'Money issues, financial stress, budgeting help',
        'keywords': ['money', 'financial', 'budget', 'debt', 'job', 'work']
    },
    'family': {
        'name': 'Family Issues',
        'icon': '👨‍👩‍👧‍👦',
        'description': 'Family conflicts, parental pressure, sibling issues',
        'keywords': ['family', 'parents', 'mother', 'father', 'sibling', 'home']
    },
    'career': {
        'name': 'Career & Future',
        'icon': '💼',
        'description': 'Career guidance, future planning, job search',
        'keywords': ['career', 'job', 'future', 'work', 'profession', 'internship']
    },
    'ministry': {
        'name': 'Ministry & Service',
        'icon': '✝️',
        'description': 'Serving in ministry, leadership, evangelism questions',
        'keywords': ['ministry', 'service', 'leadership', 'evangelism', 'mission']
    },
    'doubt': {
        'name': 'Doubt & Questions',
        'icon': '❓',
        'description': 'Doubts about faith, theological questions, confusion',
        'keywords': ['doubt', 'question', 'confusion', 'uncertain', 'why']
    },
    'crisis': {
        'name': 'Crisis & Emergency',
        'icon': '🆘',
        'description': 'Immediate help needed, suicidal thoughts, severe crisis',
        'keywords': ['crisis', 'emergency', 'suicide', 'hurt', 'danger', 'help'],
        'priority': True  # High priority matching
    },
    'general': {
        'name': 'General Counseling',
        'icon': '💬',
        'description': 'General questions, not sure which category fits',
        'keywords': ['general', 'other', 'advice', 'help', 'talk']
    }
}

class CounselingDatabase:
    def __init__(self, db_path='hu_counseling.db'):
        self.db_path = db_path
        self.init_database()
        self.migrate_add_gender_column()
    
    def get_connection(self):
        """Get database connection with proper timeout and WAL mode"""
        conn = sqlite3.connect(
            self.db_path, 
            timeout=30.0,  # Wait up to 30 seconds if database is locked
            check_same_thread=False  # Allow connection across threads
        )
        conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrency
        conn.execute('PRAGMA journal_mode=WAL')
        
        # Set busy timeout
        conn.execute('PRAGMA busy_timeout=30000')  # 30 seconds in milliseconds
        
        return conn
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table (seekers of counseling)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                gender TEXT DEFAULT 'anonymous',
                language_code TEXT DEFAULT 'en',
                is_banned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_sessions INTEGER DEFAULT 0
            )
        ''')
        
        # Counselors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS counselors (
                counselor_id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                display_name TEXT,
                bio TEXT,
                gender TEXT DEFAULT 'anonymous',
                specializations TEXT,
                status TEXT DEFAULT 'pending',
                is_available INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                rating_sum INTEGER DEFAULT 0,
                rating_count INTEGER DEFAULT 0,
                approved_by INTEGER,
                approved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Counseling sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS counseling_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                counselor_id INTEGER,
                topic TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'requested',
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                matched_at TIMESTAMP,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                end_reason TEXT,
                user_rating INTEGER,
                user_feedback TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (counselor_id) REFERENCES counselors(counselor_id)
            )
        ''')
        
        # Session messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                sender_role TEXT NOT NULL,
                sender_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES counseling_sessions(session_id)
            )
        ''')
        
        # Counselor availability table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS counselor_availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                counselor_id INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (counselor_id) REFERENCES counselors(counselor_id)
            )
        ''')
        
        # Bot statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_stats (
                stat_name TEXT PRIMARY KEY,
                stat_value INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize bot stats
        cursor.execute('''
            INSERT OR IGNORE INTO bot_stats (stat_name, stat_value) 
            VALUES 
                ('total_users', 0),
                ('total_counselors', 0),
                ('active_counselors', 0),
                ('total_sessions', 0),
                ('active_sessions', 0),
                ('completed_sessions', 0)
        ''')
        
        # Admin/moderator table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                role TEXT DEFAULT 'admin',
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.create_indexes()
        logger.info("Counseling database initialized successfully")
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_status ON counseling_sessions(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON counseling_sessions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_counselor ON counseling_sessions(counselor_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_session ON session_messages(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_counselors_status ON counselors(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_counselors_available ON counselors(is_available)')
            
            conn.commit()
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
        finally:
            conn.close()
    
    def migrate_add_gender_column(self):
        """Add gender column to existing tables if it doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if gender column exists in counselors table
            cursor.execute("PRAGMA table_info(counselors)")
            counselor_columns = [column[1] for column in cursor.fetchall()]
            
            if 'gender' not in counselor_columns:
                logger.info("Adding gender column to counselors table...")
                cursor.execute("ALTER TABLE counselors ADD COLUMN gender TEXT DEFAULT 'anonymous'")
                conn.commit()
                logger.info("Gender column added to counselors table successfully")
            else:
                logger.info("Gender column already exists in counselors table")
            
            # Check if gender column exists in users table
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [column[1] for column in cursor.fetchall()]
            
            if 'gender' not in user_columns:
                logger.info("Adding gender column to users table...")
                cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'anonymous'")
                conn.commit()
                logger.info("Gender column added to users table successfully")
            else:
                logger.info("Gender column already exists in users table")
                
        except Exception as e:
            logger.error(f"Error adding gender column: {e}")
        finally:
            conn.close()
    
    # ==================== USER MANAGEMENT ====================
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language_code: str = 'en'):
        """Add or update user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE users 
                SET username = ?, first_name = ?, last_name = ?, 
                    language_code = ?, last_active = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (username, first_name, last_name, language_code, user_id))
        else:
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, language_code)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, language_code))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_user_gender(self, user_id: int, gender: str):
        """Update user's gender"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET gender = ?
            WHERE user_id = ?
        ''', (gender, user_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"User {user_id} gender updated to {gender}")
    
    def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_banned FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row['is_banned'] == 1 if row else False
    
    # ==================== COUNSELOR MANAGEMENT ====================
    
    def register_counselor(self, user_id: int, display_name: str, bio: str, 
                          specializations: List[str], gender: str = 'anonymous') -> int:
        """Register a new counselor (pending approval)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        spec_json = json.dumps(specializations)
        
        cursor.execute('''
            INSERT INTO counselors (user_id, display_name, bio, gender, specializations, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (user_id, display_name, bio, gender, spec_json))
        
        counselor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Counselor registered: user_id={user_id}, gender={gender}")
        return counselor_id
    
    def approve_counselor(self, counselor_id: int, admin_id: int):
        """Approve a counselor application"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counselors 
            SET status = 'approved', is_available = 1, 
                approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE counselor_id = ?
        ''', (admin_id, counselor_id))
        
        cursor.execute('''
            UPDATE bot_stats 
            SET stat_value = stat_value + 1, updated_at = CURRENT_TIMESTAMP
            WHERE stat_name IN ('total_counselors', 'active_counselors')
        ''')
        
        conn.commit()
        conn.close()
    
    def reject_counselor(self, counselor_id: int):
        """Reject a counselor application"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counselors SET status = 'rejected' WHERE counselor_id = ?
        ''', (counselor_id,))
        
        conn.commit()
        conn.close()
    
    def deactivate_counselor(self, counselor_id: int, admin_id: int):
        """Temporarily deactivate a counselor (can be reactivated)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counselors 
            SET status = 'deactivated', is_available = 0
            WHERE counselor_id = ?
        ''', (counselor_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Counselor {counselor_id} deactivated by admin {admin_id}")
    
    def reactivate_counselor(self, counselor_id: int, admin_id: int):
        """Reactivate a deactivated counselor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counselors 
            SET status = 'approved', is_available = 0
            WHERE counselor_id = ?
        ''', (counselor_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Counselor {counselor_id} reactivated by admin {admin_id}")
    
    def ban_counselor(self, counselor_id: int, admin_id: int, reason: str = ''):
        """Permanently ban a counselor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counselors 
            SET status = 'banned', is_available = 0
            WHERE counselor_id = ?
        ''', (counselor_id,))
        
        # Log the ban
        conn.commit()
        conn.close()
        
        logger.warning(f"Counselor {counselor_id} BANNED by admin {admin_id}. Reason: {reason}")
    
    def update_counselor_info(self, counselor_id: int, display_name: str = None, bio: str = None, specializations: List[str] = None):
        """Update counselor information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if display_name:
            updates.append("display_name = ?")
            params.append(display_name)
        
        if bio:
            updates.append("bio = ?")
            params.append(bio)
        
        if specializations:
            updates.append("specializations = ?")
            params.append(json.dumps(specializations))
        
        if updates:
            query = f"UPDATE counselors SET {', '.join(updates)} WHERE counselor_id = ?"
            params.append(counselor_id)
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        logger.info(f"Counselor {counselor_id} info updated")
    
    def get_counselor_by_user_id(self, user_id: int) -> Optional[Dict]:
        """Get counselor data by user_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM counselors WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            data['specializations'] = json.loads(data['specializations'])
            return data
        return None
    
    def get_counselor(self, counselor_id: int) -> Optional[Dict]:
        """Get counselor data by counselor_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM counselors WHERE counselor_id = ?', (counselor_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            data['specializations'] = json.loads(data['specializations'])
            return data
        return None
    
    def set_counselor_availability(self, counselor_id: int, is_available: bool):
        """Set counselor's availability status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counselors SET is_available = ? WHERE counselor_id = ?
        ''', (1 if is_available else 0, counselor_id))
        
        conn.commit()
        conn.close()
    
    def get_available_counselors(self, topic: str = None) -> List[Dict]:
        """Get list of available counselors, optionally filtered by topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if topic:
            cursor.execute('''
                SELECT c.* FROM counselors c
                WHERE c.status = 'approved' AND c.is_available = 1
                AND NOT EXISTS (
                    SELECT 1 FROM counseling_sessions s 
                    WHERE s.counselor_id = c.counselor_id 
                    AND s.status IN ('matched', 'active')
                )
                ORDER BY c.total_sessions ASC, c.rating_sum DESC
            ''')
        else:
            cursor.execute('''
                SELECT c.* FROM counselors c
                WHERE c.status = 'approved' AND c.is_available = 1
                AND NOT EXISTS (
                    SELECT 1 FROM counseling_sessions s 
                    WHERE s.counselor_id = c.counselor_id 
                    AND s.status IN ('matched', 'active')
                )
                ORDER BY c.total_sessions ASC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        counselors = []
        for row in rows:
            data = dict(row)
            data['specializations'] = json.loads(data['specializations'])
            
            # Filter by topic if specified
            if topic and topic not in data['specializations']:
                continue
            
            counselors.append(data)
        
        return counselors
    
    def get_pending_counselors(self) -> List[Dict]:
        """Get list of pending counselor applications"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.username, u.first_name 
            FROM counselors c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.status = 'pending'
            ORDER BY c.created_at ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== SESSION MANAGEMENT ====================
    
    def create_session_request(self, user_id: int, topic: str, description: str = None) -> int:
        """Create a new counseling session request"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check for crisis keywords for priority
        priority = 0
        if topic == 'crisis':
            priority = 10
        elif description:
            crisis_keywords = ['suicide', 'kill myself', 'end my life', 'emergency', 'urgent']
            if any(word in description.lower() for word in crisis_keywords):
                priority = 10
        
        cursor.execute('''
            INSERT INTO counseling_sessions (user_id, topic, description, status, priority)
            VALUES (?, ?, ?, 'requested', ?)
        ''', (user_id, topic, description, priority))
        
        session_id = cursor.lastrowid
        
        cursor.execute('''
            UPDATE bot_stats 
            SET stat_value = stat_value + 1, updated_at = CURRENT_TIMESTAMP
            WHERE stat_name = 'total_sessions'
        ''')
        
        conn.commit()
        conn.close()
        
        return session_id
    
    @retry_on_locked(max_retries=3, delay=0.5)
    def match_session_with_counselor(self, session_id: int, counselor_id: int):
        """Match a session with a counselor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counseling_sessions 
            SET counselor_id = ?, status = 'matched', matched_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (counselor_id, session_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Session {session_id} matched with counselor {counselor_id}")
    
    @retry_on_locked(max_retries=3, delay=0.5)
    def start_session(self, session_id: int):
        """Start an active counseling session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counseling_sessions 
            SET status = 'active', started_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        
        cursor.execute('''
            UPDATE bot_stats 
            SET stat_value = stat_value + 1, updated_at = CURRENT_TIMESTAMP
            WHERE stat_name = 'active_sessions'
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Session {session_id} started successfully")
    
    def end_session(self, session_id: int, end_reason: str = 'completed'):
        """End a counseling session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counseling_sessions 
            SET status = 'ended', ended_at = CURRENT_TIMESTAMP, end_reason = ?
            WHERE session_id = ?
        ''', (end_reason, session_id))
        
        # Get session data to update stats
        cursor.execute('''
            SELECT user_id, counselor_id FROM counseling_sessions WHERE session_id = ?
        ''', (session_id,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute('''
                UPDATE users SET total_sessions = total_sessions + 1 
                WHERE user_id = ?
            ''', (row['user_id'],))
            
            if row['counselor_id']:
                cursor.execute('''
                    UPDATE counselors 
                    SET total_sessions = total_sessions + 1 
                    WHERE counselor_id = ?
                ''', (row['counselor_id'],))
        
        cursor.execute('''
            UPDATE bot_stats 
            SET stat_value = stat_value - 1, updated_at = CURRENT_TIMESTAMP
            WHERE stat_name = 'active_sessions'
        ''')
        
        cursor.execute('''
            UPDATE bot_stats 
            SET stat_value = stat_value + 1, updated_at = CURRENT_TIMESTAMP
            WHERE stat_name = 'completed_sessions'
        ''')
        
        conn.commit()
        conn.close()
    
    def get_session(self, session_id: int) -> Optional[Dict]:
        """Get session data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM counseling_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_active_session_by_user(self, user_id: int) -> Optional[Dict]:
        """Get user's active session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM counseling_sessions 
            WHERE user_id = ? AND status IN ('matched', 'active')
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_active_session_by_counselor(self, counselor_id: int) -> Optional[Dict]:
        """Get counselor's active session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM counseling_sessions 
            WHERE counselor_id = ? AND status IN ('matched', 'active')
            ORDER BY created_at DESC LIMIT 1
        ''', (counselor_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_pending_sessions(self, limit: int = 10) -> List[Dict]:
        """Get pending session requests ordered by priority"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM counseling_sessions 
            WHERE status = 'requested'
            ORDER BY priority DESC, created_at ASC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_session_rating(self, session_id: int, rating: int, feedback: str = None):
        """Add user rating for a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE counseling_sessions 
            SET user_rating = ?, user_feedback = ?
            WHERE session_id = ?
        ''', (rating, feedback, session_id))
        
        # Update counselor rating
        cursor.execute('''
            SELECT counselor_id FROM counseling_sessions WHERE session_id = ?
        ''', (session_id,))
        row = cursor.fetchone()
        
        if row and row['counselor_id']:
            cursor.execute('''
                UPDATE counselors 
                SET rating_sum = rating_sum + ?, rating_count = rating_count + 1
                WHERE counselor_id = ?
            ''', (rating, row['counselor_id']))
        
        conn.commit()
        conn.close()
    
    # ==================== MESSAGE MANAGEMENT ====================
    
    @retry_on_locked(max_retries=3, delay=0.5)
    def add_message(self, session_id: int, sender_role: str, sender_id: int, message_text: str) -> int:
        """Add a message to a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO session_messages (session_id, sender_role, sender_id, message_text)
            VALUES (?, ?, ?, ?)
        ''', (session_id, sender_role, sender_id, message_text))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_session_messages(self, session_id: int, limit: int = 100) -> List[Dict]:
        """Get messages for a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM session_messages 
            WHERE session_id = ?
            ORDER BY created_at ASC
            LIMIT ?
        ''', (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== ADMIN MANAGEMENT ====================
    
    def add_admin(self, user_id: int, added_by: int, role: str = 'admin'):
        """Add an admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO admins (user_id, role, added_by)
            VALUES (?, ?, ?)
        ''', (user_id, role, added_by))
        
        conn.commit()
        conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row is not None
    
    # ==================== STATISTICS ====================
    
    def get_bot_stats(self) -> Dict:
        """Get bot statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT stat_name, stat_value FROM bot_stats')
        rows = cursor.fetchall()
        
        stats = {row['stat_name']: row['stat_value'] for row in rows}
        
        # Get additional stats
        cursor.execute('SELECT COUNT(*) as count FROM users')
        stats['total_users'] = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM users 
            WHERE DATE(last_active) = DATE('now')
        ''')
        stats['active_today'] = cursor.fetchone()['count']
        
        conn.close()
        return stats
