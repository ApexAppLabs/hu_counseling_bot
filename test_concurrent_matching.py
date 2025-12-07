#!/usr/bin/env python3
"""
Test script to demonstrate the concurrent matching issue
This shows how counselors with active sessions can still be matched to new users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from counseling_database import CounselingDatabase
from matching_system import CounselingMatcher

def test_concurrent_matching_issue():
    """Test that demonstrates the concurrent matching bug"""
    
    print("🔍 Testing Concurrent Matching Issue")
    print("=" * 50)
    
    db = CounselingDatabase()
    matcher = CounselingMatcher(db)
    
    # Get available counselors for a topic (e.g., 'academic')
    topic = 'academic'
    print(f"\n📋 Getting available counselors for topic: {topic}")
    
    available_counselors = db.get_available_counselors(topic)
    print(f"Found {len(available_counselors)} 'available' counselors:")
    
    for counselor in available_counselors:
        counselor_id = counselor['counselor_id']
        print(f"\n👨‍⚕️ Counselor {counselor_id}:")
        print(f"   Status: {counselor['status']}")
        print(f"   Available: {counselor['is_available']}")
        print(f"   Specializations: {counselor['specializations']}")
        
        # Check if this counselor has an active session
        active_session = db.get_active_session_by_counselor(counselor_id)
        if active_session:
            print(f"   ⚠️  ACTIVE SESSION: {active_session['session_id']} (status: {active_session['status']})")
            print(f"   🚨 THIS COUNSELOR SHOULD NOT BE AVAILABLE FOR MATCHING!")
        else:
            print(f"   ✅ No active sessions")
    
    print(f"\n🎯 Testing matching algorithm...")
    
    # Get pending sessions
    pending_sessions = db.get_pending_sessions(limit=5)
    if pending_sessions:
        session = pending_sessions[0]
        session_id = session['session_id']
        print(f"📝 Testing with session {session_id} (topic: {session['topic']})")
        
        best_match = matcher.find_best_match(session_id)
        if best_match:
            matched_counselor = db.get_counselor(best_match)
            active_session = db.get_active_session_by_counselor(best_match)
            
            print(f"\n🎲 Matcher selected counselor {best_match}")
            if active_session:
                print(f"🚨 CRITICAL BUG: Matched counselor already has active session {active_session['session_id']}")
                print(f"   This creates multiple concurrent sessions for the same counselor!")
            else:
                print(f"✅ Matched counselor has no active sessions (good)")
        else:
            print("❌ No match found")
    else:
        print("ℹ️  No pending sessions to test with")
    
    print(f"\n📊 Summary:")
    print(f"   The get_available_counselors() method does not filter out counselors with active sessions")
    print(f"   This leads to counselors being matched to multiple users simultaneously")
    print(f"   Fix: Update the SQL query to exclude counselors with active sessions")

if __name__ == '__main__':
    test_concurrent_matching_issue()
