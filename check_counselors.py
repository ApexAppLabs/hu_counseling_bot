#!/usr/bin/env python3
"""
Script to check counselor availability and current assignments
"""

from counseling_database import CounselingDatabase

def check_counselors():
    # Connect to database
    db = CounselingDatabase()
    
    # Get all counselors
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM counselors WHERE status = "approved"')
    counselors = cursor.fetchall()
    
    print("=== ALL APPROVED COUNSELORS ===")
    for counselor in counselors:
        print(f"Counselor {counselor['counselor_id']}:")
        print(f"  User ID: {counselor['user_id']}")
        print(f"  Specializations: {counselor['specializations']}")
        print(f"  Available: {counselor['is_available']}")
        
        # Check if counselor has active sessions
        cursor.execute('SELECT * FROM counseling_sessions WHERE counselor_id = ? AND status IN ("matched", "active")', 
                      (counselor['counselor_id'],))
        active_sessions = cursor.fetchall()
        print(f"  Active sessions: {len(active_sessions)}")
        for session in active_sessions:
            print(f"    Session {session['session_id']}: {session['topic']} ({session['status']})")
        print()
    
    # Check pending sessions
    cursor.execute('SELECT * FROM counseling_sessions WHERE status = "requested" ORDER BY session_id')
    pending_sessions = cursor.fetchall()
    
    print("=== PENDING SESSIONS ===")
    for session in pending_sessions:
        print(f"Session {session['session_id']}: {session['topic']} (User: {session['user_id']})")
    
    conn.close()

if __name__ == "__main__":
    check_counselors()