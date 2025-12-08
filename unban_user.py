import os
import psycopg2

# Set your DATABASE_URL or use environment variable
DATABASE_URL = os.getenv("DATABASE_URL")  # Ensure this is set in your environment
USER_ID = int(input("Enter the Telegram user_id to unban: "))

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in environment")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Update ban status
    cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = %s", (USER_ID,))
    if cursor.rowcount == 0:
        print(f"No user found with user_id = {USER_ID}")
    else:
        print(f"Unbanned user_id {USER_ID}")

    # Verify
    cursor.execute("SELECT is_banned FROM users WHERE user_id = %s", (USER_ID,))
    row = cursor.fetchone()
    if row:
        print(f"Current ban status: {row[0]}")
    else:
        print("User not found after update")

    conn.commit()
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
