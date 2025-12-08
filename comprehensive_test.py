#!/usr/bin/env python3
"""
Comprehensive test to verify the matching system works for all categories
"""

from counseling_database import CounselingDatabase, COUNSELING_TOPICS
from matching_system import CounselingMatcher

def comprehensive_test():
    print("=== COMPREHENSIVE MATCHING TEST ===")
    
    # Initialize database and matcher
    db = CounselingDatabase()
    matcher = CounselingMatcher(db)
    
    # Test each category
    all_passed = True
    for topic_key, topic_data in COUNSELING_TOPICS.items():
        print(f"\nTesting: {topic_data['icon']} {topic_data['name']}")
        
        # Create a test session
        session_id = db.create_session_request(123456789, topic_key, "Test description for " + topic_data['name'])
        print(f"  Created session {session_id}")
        
        # Try to find a match
        counselor_id = matcher.find_best_match(session_id)
        if counselor_id:
            print(f"  ✓ MATCH FOUND: Counselor {counselor_id}")
            
            # Verify the counselor has this specialization
            counselor = db.get_counselor(counselor_id)
            if topic_key in counselor['specializations']:
                print(f"  ✓ Counselor properly specialized in {topic_key}")
            else:
                print(f"  ✗ ERROR: Counselor {counselor_id} not specialized in {topic_key}")
                print(f"    Specializations: {counselor['specializations']}")
                all_passed = False
        else:
            print(f"  ✗ NO MATCH FOUND")
            all_passed = False
        
        # Clean up the test session
        db.end_session(session_id, "test_cleanup")
        print(f"  Cleaned up session {session_id}")
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The system is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! There are issues to address.")
    print("="*50)

if __name__ == "__main__":
    comprehensive_test()