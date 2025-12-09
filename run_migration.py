"""
Run database migration to remove verification system and add flagging
"""
import pymysql
import yaml
from pathlib import Path

# Load config
config = yaml.safe_load(Path('config.yml').read_text())

# Connect to database
connection = pymysql.connect(
    host=config['db']['host'],
    user=config['db']['user'],
    password=config['db']['pw'],
    database=config['db']['db'],
    cursorclass=pymysql.cursors.DictCursor
)

print("Connected to database successfully!")

try:
    with connection.cursor() as cursor:
        # Read migration file
        with open('migration_remove_verification.sql', 'r') as f:
            sql_commands = f.read()

        # Split by semicolon and execute each command
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip() and not cmd.strip().startswith('--')]

        total = len(commands)
        for i, command in enumerate(commands, 1):
            # Skip comments
            if command.startswith('--') or command.upper().startswith('DESCRIBE') or command.upper().startswith('SELECT'):
                continue

            try:
                print(f"[{i}/{total}] Executing: {command[:80]}...")
                cursor.execute(command)
                connection.commit()
                print(f"    [OK] Success")
            except Exception as e:
                # Some errors are okay (like column already exists or doesn't exist)
                if 'already exists' in str(e) or "Can't DROP" in str(e) or "Unknown column" in str(e):
                    print(f"    [SKIP] Already applied: {str(e)[:100]}")
                else:
                    print(f"    [ERROR] {e}")
                    raise

    print("\n[SUCCESS] Migration completed successfully!")
    print("\nVerifying changes...")

    # Verify the changes
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_type, COUNT(*) as count FROM Users GROUP BY user_type")
        print("\nUsers by type:")
        for row in cursor.fetchall():
            print(f"  - {row['user_type']}: {row['count']}")

        cursor.execute("SELECT COUNT(*) FROM Locations WHERE is_flagged = 1")
        flagged = cursor.fetchone()['COUNT(*)']
        print(f"\nFlagged locations: {flagged}")

        cursor.execute("SELECT COUNT(*) FROM Locations")
        total_locations = cursor.fetchone()['COUNT(*)']
        print(f"Total locations: {total_locations}")

finally:
    connection.close()
    print("\n[SUCCESS] Database connection closed.")
