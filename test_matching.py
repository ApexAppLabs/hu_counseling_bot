#!/usr/bin/env python3
"""
Test script to verify the matching system works correctly after updating counselor specializations
"""

from counseling_database import CounselingDatabase, COUNSELING_TOPICS
from matching_system import CounselingMatcher

def test_matching():
    # Initialize database and matcher
    db = CounselingDatabase()
    matcher = CounselingMatcher(db)
    
    print("=== Testing Matching System ===")
    print(f"Current topic categories: {list(COUNSELING_TOPICS.keys())}")
    
    # Get available counselors
    counselors = db.get_available_counselors()
    print(f"\nAvailable counselors: {len(counselors)}")
    for counselor in counselors:
        print(f"  Counselor {counselor['counselor_id']}: {counselor['specializations']}")
    
    # Test matching for each topic
    print("\n=== Testing Matching for Each Topic ===")
    for topic_key in COUNSELING_TOPICS.keys():
        print(f"\nTesting topic: {topic_key}")
        # Create a test session
        session_id = db.create_session_request(123456789, topic_key, "Test description")
        print(f"  Created test session: {session_id}")
        
        # Try to find a match
        counselor_id = matcher.find_best_match(session_id)
        if counselor_id:
            print(f"  ✓ Match found: Counselor {counselor_id}")
        else:
            print(f"  ✗ No match found")
        
        # Clean up the test session
        db.end_session(session_id, "test_cleanup")
    
    # Test with crisis topic specifically (high priority)
    print("\n=== Testing Crisis Topic (High Priority) ===")
    session_id = db.create_session_request(123456789, "crisis_substance", "Emergency situation")
    counselor_id = matcher.find_best_match(session_id)
    if counselor_id:
        print(f"  ✓ Crisis match found: Counselor {counselor_id} (should be counselor 2)")
    else:
        print(f"  ✗ No crisis match found")
    db.end_session(session_id, "test_cleanup")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_matching()