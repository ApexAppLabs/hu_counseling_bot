#!/usr/bin/env python3
"""
Test script to verify the concurrent matching fix
This confirms that counselors with active sessions are properly excluded
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from counseling_database import CounselingDatabase
from matching_system import CounselingMatcher

def test_concurrent_matching_fix():
    """Test that verifies the concurrent matching fix works"""
    
    print("🔧 Testing Concurrent Matching Fix")
    print("=" * 50)
    
    db = CounselingDatabase()
    matcher = CounselingMatcher(db)
    
    # Get available counselors for a topic (e.g., 'academic')
    topic = 'academic'
    print(f"\n📋 Getting available counselors for topic: {topic}")
    
    available_counselors = db.get_available_counselors(topic)
    print(f"Found {len(available_counselors)} truly available counselors:")
    
    all_clear = True
    for counselor in available_counselors:
        counselor_id = counselor['counselor_id']
        print(f"\n👨‍⚕️ Counselor {counselor_id}:")
        print(f"   Status: {counselor['status']}")
        print(f"   Available: {counselor['is_available']}")
        print(f"   Specializations: {counselor['specializations']}")
        
        # Check if this counselor has an active session
        active_session = db.get_active_session_by_counselor(counselor_id)
        if active_session:
            print(f"   🚨 ACTIVE SESSION FOUND: {active_session['session_id']} (status: {active_session['status']})")
            print(f"   ❌ FIX FAILED: Counselor with active session is still considered available!")
            all_clear = False
        else:
            print(f"   ✅ No active sessions (correctly excluded)")
    
    print(f"\n🎯 Testing matching algorithm with fix...")
    
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
                print(f"🚨 FIX FAILED: Matched counselor has active session {active_session['session_id']}")
                all_clear = False
            else:
                print(f"✅ SUCCESS: Matched counselor has no active sessions")
        else:
            print("ℹ️  No match found (no available counselors)")
    else:
        print("ℹ️  No pending sessions to test with")
    
    print(f"\n📊 Fix Verification Result:")
    if all_clear:
        print("   ✅ FIX SUCCESSFUL: Counselors with active sessions are properly excluded")
        print("   ✅ Concurrent matching issue has been resolved")
    else:
        print("   ❌ FIX FAILED: Some counselors with active sessions are still being matched")
    
    return all_clear

if __name__ == '__main__':
    success = test_concurrent_matching_fix()
    sys.exit(0 if success else 1)
