import sqlite3

def check_all_tables():
    conn = sqlite3.connect('hu_counseling.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\'')
    tables = [row[0] for row in cursor.fetchall()]
    print('All tables:', tables)

    # Check each table for potential session-related data
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'{table}: {count} records')

    conn.close()

if __name__ == "__main__":
    check_all_tables()