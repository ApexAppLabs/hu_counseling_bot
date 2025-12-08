#!/usr/bin/env python3
"""
Diagnostic script for Render deployment
This script can be run on Render to check the database status
"""

from counseling_database import CounselingDatabase, COUNSELING_TOPICS
from matching_system import CounselingMatcher

def diagnose_render_deployment():
    print("=== RENDER DEPLOYMENT DIAGNOSTIC ===\n")
    
    # Initialize database
    db = CounselingDatabase()
    matcher = CounselingMatcher(db)
    
    print("1. DATABASE INFO:")
    print(f"   Database path: {db.db_path}")
    print(f"   Using PostgreSQL: {'Yes' if hasattr(db, 'USE_POSTGRES') and db.USE_POSTGRES else 'No'}")
    
    # Check counselors
    print("\n2. COUNSELOR STATUS:")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM counselors')
    total_counselors = cursor.fetchone()['count']
    print(f"   Total counselors: {total_counselors}")
    
    cursor.execute("SELECT COUNT(*) as count FROM counselors WHERE status='approved'")
    approved_counselors = cursor.fetchone()['count']
    print(f"   Approved counselors: {approved_counselors}")
    
    cursor.execute("SELECT COUNT(*) as count FROM counselors WHERE status='approved' AND is_available=1")
    available_counselors = cursor.fetchone()['count']
    print(f"   Available counselors: {available_counselors}")
    
    # Show counselor details
    if total_counselors > 0:
        print("\n   COUNSELOR DETAILS:")
        cursor.execute('SELECT * FROM counselors')
        counselors = cursor.fetchall()
        for c in counselors:
            print(f"   - Counselor {c['counselor_id']} (User: {c['user_id']})")
            print(f"     Status: {c['status']}")
            print(f"     Available: {'Yes' if c['is_available'] else 'No'}")
            print(f"     Specializations: {c['specializations']}")
            print()
    
    conn.close()
    
    # Check topic categories
    print("3. TOPIC CATEGORIES:")
    for key, data in COUNSELING_TOPICS.items():
        print(f"   {data['icon']} {data['name']} ({key})")
    
    # Test matching for each category
    print("\n4. MATCHING TEST:")
    all_passed = True
    for topic_key, topic_data in COUNSELING_TOPICS.items():
        print(f"   Testing {topic_data['icon']} {topic_data['name']}...")
        
        # Create a test session
        session_id = db.create_session_request(123456789, topic_key, "Test")
        
        # Try to find a match
        counselor_id = matcher.find_best_match(session_id)
        if counselor_id:
            print(f"     ✓ Match found: Counselor {counselor_id}")
        else:
            print(f"     ✗ No match found")
            all_passed = False
        
        # Clean up
        db.end_session(session_id, "diagnostic_cleanup")
    
    print("\n5. SUMMARY:")
    if all_passed and available_counselors > 0:
        print("   🎉 All systems working correctly!")
    elif available_counselors == 0:
        print("   ⚠️  No counselors available - this is likely why users see 'No available counselors'")
        print("   SOLUTION: Approve pending counselors and/or toggle availability")
    else:
        print("   ❌ Some issues detected - check the matching test results above")
    
    print("\n=== END DIAGNOSTIC ===")

if __name__ == "__main__":
    diagnose_render_deployment()