#!/usr/bin/env python3
"""
Script to check counselor specializations
"""

from counseling_database import CounselingDatabase
import json

def check_counselor_specializations():
    db = CounselingDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT counselor_id, specializations FROM counselors WHERE status = "approved"')
    counselors = cursor.fetchall()
    
    print("Current counselor specializations:")
    for counselor in counselors:
        specs = json.loads(counselor[1])
        print(f"Counselor {counselor[0]}: {specs}")
    
    conn.close()

if __name__ == "__main__":
    check_counselor_specializations()