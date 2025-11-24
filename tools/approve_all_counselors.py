"""
Quick script to approve all pending counselors and make them available
Use this for testing purposes
"""

from counseling_database import CounselingDatabase

db = CounselingDatabase()

print("\n=== APPROVING ALL COUNSELORS ===\n")

# Get all pending counselors
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("SELECT * FROM counselors WHERE status='pending'")
pending = cursor.fetchall()

if not pending:
    print("No pending counselors to approve.")
else:
    print(f"Found {len(pending)} pending counselor(s):\n")
    for c in pending:
        print(f"- {c['display_name']} (User ID: {c['user_id']})")
    
    print("\nApproving...")
    
    # Approve all pending
    cursor.execute("""
        UPDATE counselors 
        SET status='approved', is_available=1, approved_at=CURRENT_TIMESTAMP 
        WHERE status='pending'
    """)
    
    conn.commit()
    print(f"\n[OK] Approved {cursor.rowcount} counselor(s)")
    print("[OK] Set all to AVAILABLE")

conn.close()

# Verify
print("\n=== VERIFICATION ===\n")
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT * FROM counselors 
    WHERE status='approved' AND is_available=1
""")
ready = cursor.fetchall()

print(f"Ready counselors (Approved + Available): {len(ready)}\n")
for c in ready:
    specs = eval(c['specializations']) if c['specializations'] else []
    print(f"[OK] {c['display_name']}")
    print(f"   User ID: {c['user_id']}")
    print(f"   Specializations: {', '.join(specs)}")
    print()

conn.close()

print("[DONE] Users can now request counseling!\n")
