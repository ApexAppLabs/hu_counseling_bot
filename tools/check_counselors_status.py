from counseling_database import CounselingDatabase

db = CounselingDatabase()

print("\n=== COUNSELOR STATUS CHECK ===\n")

# Get all counselors
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute('SELECT * FROM counselors')
counselors = cursor.fetchall()
conn.close()

if not counselors:
    print("❌ NO COUNSELORS REGISTERED!")
    print("\nYou need to:")
    print("1. Register as a counselor using the bot")
    print("2. Admin must approve the counselor")
    print("3. Counselor must toggle availability ON")
else:
    print(f"Total Counselors: {len(counselors)}\n")
    
    for c in counselors:
        print(f"--- Counselor ID: {c['counselor_id']} ---")
        print(f"User ID: {c['user_id']}")
        print(f"Display Name: {c['display_name'] or 'Not set'}")
        print(f"Status: {c['status']}")
        print(f"Available: {'YES' if c['is_available'] else 'NO'}")
        print(f"Specializations: {c['specializations']}")
        print(f"Total Sessions: {c['total_sessions']}")
        print()

# Check for approved + available counselors
cursor = conn.cursor()
cursor.execute('''
    SELECT COUNT(*) as count 
    FROM counselors 
    WHERE status = 'approved' AND is_available = 1
''')
available_count = cursor.fetchone()['count']
conn.close()

print(f"\n✅ READY COUNSELORS (Approved + Available): {available_count}")

if available_count == 0:
    print("\n⚠️ THIS IS WHY USERS SEE 'No available counselors'")
    print("\nTO FIX:")
    print("1. If no counselors exist: Someone must register as counselor")
    print("2. If counselors exist but pending: Admin must approve them (/admin command)")
    print("3. If counselors approved but not available: Counselor must toggle availability ON")
