#!/usr/bin/env python3
"""
Fix Bad Sessions Tool
Resolves invalid sessions where user and counselor are the same person
"""

import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from counseling_database import CounselingDatabase

print("=" * 60)
print("HU Counseling Bot - Fix Bad Sessions Tool")
print("=" * 60)
print()

# Initialize database
try:
    db = CounselingDatabase()
    print("✅ Database connected successfully")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

# Find bad sessions where user_id equals counselor's user_id
print("\n🔍 Finding bad sessions...")
conn = db.get_connection()
cursor = conn.cursor()

# Import the param_placeholder
ph = db.param_placeholder

cursor.execute(f"""
    SELECT s.session_id, s.user_id, c.user_id as counselor_user_id
    FROM counseling_sessions s
    JOIN counselors c ON s.counselor_id = c.counselor_id
    WHERE s.user_id = c.user_id
""")

bad_sessions = cursor.fetchall()
print(f"Found {len(bad_sessions)} bad session(s)")

# Fix bad sessions
if bad_sessions:
    print("\n🔧 Fixing bad sessions...")
    for session in bad_sessions:
        session_id = session['session_id']
        print(f"  Fixing session {session_id}...")
        
        cursor.execute(f"""
            UPDATE counseling_sessions 
            SET status = 'completed', 
                end_reason = 'Invalid session - counselor was also user',
                ended_at = CURRENT_TIMESTAMP
            WHERE session_id = {ph}
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