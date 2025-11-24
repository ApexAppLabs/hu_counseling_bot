"""
Fix the bad session where counselor is chatting with themselves
This happens when a counselor also requests counseling
"""

from counseling_database import CounselingDatabase

db = CounselingDatabase()

print("=" * 60)
print("FIXING BAD SESSIONS")
print("=" * 60)

# Find sessions where user_id matches counselor's user_id
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT s.session_id, s.user_id, s.counselor_id, s.status,
           c.user_id as counselor_user_id, c.display_name
    FROM counseling_sessions s
    JOIN counselors c ON s.counselor_id = c.counselor_id
    WHERE s.user_id = c.user_id
    AND s.status IN ('matched', 'active')
""")

bad_sessions = cursor.fetchall()

if not bad_sessions:
    print("\n✅ No bad sessions found! All sessions are valid.")
else:
    print(f"\n❌ Found {len(bad_sessions)} bad session(s):\n")
    
    for session in bad_sessions:
        print(f"Session ID: {session['session_id']}")
        print(f"  User ID: {session['user_id']}")
        print(f"  Counselor User ID: {session['counselor_user_id']}")
        print(f"  Status: {session['status']}")
        print(f"  Problem: Counselor is talking to themselves!")
        print()
    
    print("=" * 60)
    print("FIXING...")
    print("=" * 60)
    
    for session in bad_sessions:
        session_id = session['session_id']
        
        # End this bad session
        cursor.execute("""
            UPDATE counseling_sessions 
            SET status = 'completed', 
                end_reason = 'Invalid session - counselor was also user',
                ended_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        
        print(f"✅ Ended session {session_id}")
    
    conn.commit()
    print(f"\n✅ Fixed {len(bad_sessions)} bad session(s)")

conn.close()

print("\n" + "=" * 60)
print("CURRENT ACTIVE SESSIONS:")
print("=" * 60)

# Show remaining active sessions
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT s.session_id, s.user_id, s.counselor_id, s.status,
           c.user_id as counselor_user_id
    FROM counseling_sessions s
    JOIN counselors c ON s.counselor_id = c.counselor_id
    WHERE s.status IN ('matched', 'active')
""")

active_sessions = cursor.fetchall()

if not active_sessions:
    print("\nNo active sessions")
else:
    for session in active_sessions:
        print(f"\nSession {session['session_id']}:")
        print(f"  User: {session['user_id']}")
        print(f"  Counselor: {session['counselor_user_id']}")
        print(f"  Status: {session['status']}")
        
        if session['user_id'] == session['counselor_user_id']:
            print(f"  ⚠️ WARNING: Still has same user/counselor!")
        else:
            print(f"  ✅ Valid session")

conn.close()

print("\n" + "=" * 60)
print("DONE!")
print("=" * 60)
print("\nNow restart your bot and test counselor messages again!")
