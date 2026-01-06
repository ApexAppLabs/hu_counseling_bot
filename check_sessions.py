from counseling_database import CounselingDatabase

def check_session_counts():
    db = CounselingDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Get real-time session counts
        cursor.execute('SELECT status, COUNT(*) FROM counseling_sessions GROUP BY status')
        results = cursor.fetchall()
        print('Current session status counts:')
        for status, count in results:
            print(f'  {status}: {count}')

        # Check total sessions
        cursor.execute('SELECT COUNT(*) FROM counseling_sessions')
        total = cursor.fetchone()[0]
        print(f'Total sessions: {total}')

        # Check bot stats
        cursor.execute("SELECT stat_name, stat_value FROM bot_stats WHERE stat_name LIKE '%session%'")
        stats = cursor.fetchall()
        print('\nBot stats:')
        for stat_name, stat_value in stats:
            print(f'  {stat_name}: {stat_value}')
    finally:
        conn.close()

if __name__ == "__main__":
    check_session_counts()