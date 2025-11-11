"""
Advanced Matching System for HU Counseling Service
Intelligently matches users with the best available counselor
"""

import logging
from typing import Optional, Dict, List, Tuple
from counseling_database import CounselingDatabase, COUNSELING_TOPICS
import random

logger = logging.getLogger(__name__)

class CounselingMatcher:
    """
    Advanced matching algorithm with multiple strategies:
    1. Priority-based (crisis situations get immediate attention)
    2. Specialization matching (counselors with relevant expertise)
    3. Load balancing (distribute sessions fairly)
    4. Rating-based (prefer higher-rated counselors)
    5. Availability-based (only match available counselors)
    """
    
    def __init__(self, db: CounselingDatabase):
        self.db = db
    
    def find_best_match(self, session_id: int) -> Optional[int]:
        """
        Find the best counselor for a session using advanced matching algorithm
        Returns: counselor_id or None if no match found
        """
        session = self.db.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        topic = session['topic']
        priority = session.get('priority', 0)
        
        # Get available counselors
        available_counselors = self.db.get_available_counselors(topic)
        
        if not available_counselors:
            logger.warning(f"No available counselors for topic: {topic}")
            return None
        
        # Score each counselor
        scored_counselors = []
        for counselor in available_counselors:
            score = self._calculate_counselor_score(counselor, topic, priority)
            scored_counselors.append((counselor['counselor_id'], score, counselor))
        
        # Sort by score (highest first)
        scored_counselors.sort(key=lambda x: x[1], reverse=True)
        
        # Log the matching decision
        logger.info(f"Matching session {session_id} (topic: {topic}, priority: {priority})")
        logger.info(f"Top 3 counselors: {[(c[0], c[1]) for c in scored_counselors[:3]]}")
        
        # Return the best match
        best_counselor_id = scored_counselors[0][0]
        return best_counselor_id
    
    def _calculate_counselor_score(self, counselor: Dict, topic: str, priority: int) -> float:
        """
        Calculate a score for how well a counselor matches a session
        Higher score = better match
        """
        score = 0.0
        
        # 1. Specialization match (0-40 points)
        specializations = counselor.get('specializations', [])
        if topic in specializations:
            score += 40
            
            # Bonus if it's their primary specialization (first in list)
            if specializations and specializations[0] == topic:
                score += 10
        else:
            # Partial credit for general counseling
            if 'general' in specializations:
                score += 20
        
        # 2. Load balancing - prefer counselors with fewer sessions (0-20 points)
        # Inverse relationship: fewer sessions = higher score
        total_sessions = counselor.get('total_sessions', 0)
        if total_sessions == 0:
            score += 20  # New counselors get priority
        else:
            # Scale: 20 points for 0 sessions, decreasing as sessions increase
            score += max(0, 20 - (total_sessions * 0.5))
        
        # 3. Rating quality (0-20 points)
        rating_count = counselor.get('rating_count', 0)
        rating_sum = counselor.get('rating_sum', 0)
        
        if rating_count > 0:
            avg_rating = rating_sum / rating_count
            # Scale: 4-20 points based on 1-5 star rating
            score += (avg_rating / 5.0) * 20
        else:
            # New counselors with no ratings get neutral score
            score += 12  # Midpoint
        
        # 4. Experience bonus (0-10 points)
        # Counselors with 5+ sessions get experience bonus
        if total_sessions >= 5:
            score += min(10, total_sessions * 0.5)
        
        # 5. Crisis handling (0-10 bonus points)
        # If this is a crisis, prioritize counselors specialized in crisis
        if priority >= 10:
            if 'crisis' in specializations or 'mental_health' in specializations:
                score += 10
        
        return score
    
    def auto_match_pending_sessions(self) -> List[Tuple[int, int]]:
        """
        Automatically match all pending sessions with available counselors
        Returns: List of (session_id, counselor_id) tuples
        """
        pending_sessions = self.db.get_pending_sessions(limit=50)
        matched_pairs = []
        
        for session in pending_sessions:
            session_id = session['session_id']
            counselor_id = self.find_best_match(session_id)
            
            if counselor_id:
                # Match the session
                self.db.match_session_with_counselor(session_id, counselor_id)
                matched_pairs.append((session_id, counselor_id))
                
                logger.info(f"Auto-matched session {session_id} with counselor {counselor_id}")
        
        return matched_pairs
    
    def get_counselor_workload(self, counselor_id: int) -> Dict:
        """
        Get current workload statistics for a counselor
        """
        counselor = self.db.get_counselor(counselor_id)
        if not counselor:
            return {}
        
        active_session = self.db.get_active_session_by_counselor(counselor_id)
        
        return {
            'counselor_id': counselor_id,
            'total_sessions': counselor.get('total_sessions', 0),
            'has_active_session': active_session is not None,
            'average_rating': self._get_average_rating(counselor),
            'is_available': counselor.get('is_available', False)
        }
    
    def _get_average_rating(self, counselor: Dict) -> float:
        """Calculate average rating for a counselor"""
        rating_count = counselor.get('rating_count', 0)
        rating_sum = counselor.get('rating_sum', 0)
        
        if rating_count == 0:
            return 0.0
        
        return round(rating_sum / rating_count, 2)
    
    def get_matching_statistics(self) -> Dict:
        """
        Get statistics about the matching system performance
        """
        stats = self.db.get_bot_stats()
        
        # Calculate matching efficiency
        total_sessions = stats.get('total_sessions', 0)
        completed_sessions = stats.get('completed_sessions', 0)
        
        if total_sessions > 0:
            completion_rate = (completed_sessions / total_sessions) * 100
        else:
            completion_rate = 0.0
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': stats.get('active_sessions', 0),
            'completed_sessions': completed_sessions,
            'completion_rate': round(completion_rate, 2),
            'active_counselors': stats.get('active_counselors', 0),
            'total_counselors': stats.get('total_counselors', 0)
        }
    
    def suggest_specializations_for_user(self, description: str) -> List[str]:
        """
        Analyze user's description and suggest relevant topics
        Uses keyword matching from COUNSELING_TOPICS
        """
        description_lower = description.lower()
        suggestions = []
        
        for topic_key, topic_data in COUNSELING_TOPICS.items():
            keywords = topic_data.get('keywords', [])
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword in description_lower:
                    suggestions.append(topic_key)
                    break
        
        # Remove duplicates and limit to top 3
        suggestions = list(dict.fromkeys(suggestions))[:3]
        
        # If no matches, suggest general
        if not suggestions:
            suggestions = ['general']
        
        return suggestions
    
    def notify_match(self, session_id: int) -> Tuple[int, int]:
        """
        Get user_id and counselor_user_id for sending notifications
        Returns: (user_id, counselor_user_id)
        """
        session = self.db.get_session(session_id)
        if not session:
            return (None, None)
        
        user_id = session['user_id']
        counselor_id = session.get('counselor_id')
        
        if not counselor_id:
            return (user_id, None)
        
        counselor = self.db.get_counselor(counselor_id)
        counselor_user_id = counselor['user_id'] if counselor else None
        
        return (user_id, counselor_user_id)
    
    def get_topic_distribution(self) -> Dict[str, int]:
        """
        Get distribution of sessions by topic
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT topic, COUNT(*) as count 
            FROM counseling_sessions 
            GROUP BY topic
            ORDER BY count DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return {row['topic']: row['count'] for row in rows}
    
    def recommend_counselor_training(self) -> List[str]:
        """
        Recommend topics that need more counselor coverage
        """
        topic_dist = self.get_topic_distribution()
        
        # Get all counselors and their specializations
        available = self.db.get_available_counselors()
        
        specialization_count = {}
        for counselor in available:
            for spec in counselor['specializations']:
                specialization_count[spec] = specialization_count.get(spec, 0) + 1
        
        # Find topics with high demand but low counselor coverage
        recommendations = []
        for topic, session_count in topic_dist.items():
            counselor_count = specialization_count.get(topic, 0)
            
            # If more than 5 sessions but less than 2 counselors
            if session_count >= 5 and counselor_count < 2:
                recommendations.append(topic)
        
        return recommendations
