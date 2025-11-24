"""
Debug script to check active sessions and message routing
Run this while bot is running to see what's happening
"""

from counseling_database import CounselingDatabase

db = CounselingDatabase()

print("=" * 60)
print("SESSION DEBUGGING TOOL")
print("=" * 60)

# Get all active sessions
conn = db.get_connection()
cursor = conn.cursor()

print("\n1. ACTIVE SESSIONS:")
print("-" * 60)
cursor.execute("""
    SELECT session_id, user_id, counselor_id, topic, status, started_at
    FROM counseling_sessions 
    WHERE status IN ('matched', 'active')
    ORDER BY session_id DESC
""")
sessions = cursor.fetchall()

if not sessions:
    print("   No active sessions found")
else:
    for s in sessions:
        print(f"\n   Session ID: {s['session_id']}")
        print(f"   User ID: {s['user_id']}")
        print(f"   Counselor ID: {s['counselor_id']}")
        print(f"   Topic: {s['topic']}")
        print(f"   Status: {s['status']}")
        print(f"   Started: {s['started_at']}")
        
        # Get counselor details
        counselor = db.get_counselor(s['counselor_id'])
        if counselor:
            print(f"   Counselor User ID: {counselor['user_id']}")
            print(f"   Counselor Status: {counselor.get('status', 'unknown')}")
        
        # Get message count
        cursor.execute("""
            SELECT COUNT(*) as count, sender_role
            FROM session_messages 
            WHERE session_id = ?
            GROUP BY sender_role
        """, (s['session_id'],))
        messages = cursor.fetchall()
        
        print(f"   Messages:")
        for m in messages:
            print(f"      {m['sender_role']}: {m['count']} messages")

print("\n\n2. ALL COUNSELORS:")
print("-" * 60)
cursor.execute("""
    SELECT counselor_id, user_id, display_name, status, is_available
    FROM counselors
    ORDER BY counselor_id
""")
counselors = cursor.fetchall()

if not counselors:
    print("   No counselors found")
else:
    for c in counselors:
        avail = "🟢 Online" if c['is_available'] else "🔴 Offline"
        status = c['status']
        print(f"\n   Counselor ID: {c['counselor_id']}")
        print(f"   User ID: {c['user_id']}")
        print(f"   Name: {c['display_name']}")
        print(f"   Status: {status}")
        print(f"   Availability: {avail}")

print("\n\n3. RECENT MESSAGES:")
print("-" * 60)
cursor.execute("""
    SELECT m.message_id, m.session_id, m.sender_role, m.sender_id, 
           substr(m.message_text, 1, 50) as preview, m.created_at
    FROM session_messages m
    JOIN counseling_sessions s ON m.session_id = s.session_id
    WHERE s.status IN ('matched', 'active')
    ORDER BY m.created_at DESC
    LIMIT 20
""")
messages = cursor.fetchall()

if not messages:
    print("   No recent messages in active sessions")
else:
    for m in messages:
        print(f"\n   Message ID: {m['message_id']}")
        print(f"   Session: {m['session_id']}")
        print(f"   From: {m['sender_role']} (ID: {m['sender_id']})")
        print(f"   Preview: {m['preview']}...")
        print(f"   Time: {m['created_at']}")

conn.close()

print("\n" + "=" * 60)
print("DEBUGGING TIPS:")
print("=" * 60)
print("""
1. Check if counselor status is 'approved' (must be!)
2. Verify counselor User ID matches Telegram account
3. Ensure session status is 'active' (not just 'matched')
4. Check if messages are being saved to database
5. Look at bot logs for errors when counselor sends message

To check bot logs while running:
- Look at console output for ERROR messages
- Check for: "Counselor X sent message to user Y"
- If you don't see this log, message isn't being sent

Common issues:
- Counselor not approved → Fix: Use Admin Panel
- Session status still 'matched' → Fix: Counselor needs to accept
- Wrong user ID → Fix: Verify IDs match
""")
print("=" * 60)
