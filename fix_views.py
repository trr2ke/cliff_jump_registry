"""
Check and fix database views after migration
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

print("Connected to database successfully!\n")

try:
    with connection.cursor() as cursor:
        # Find all views
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = cursor.fetchall()

        print(f"Found {len(views)} view(s):\n")
        for view in views:
            view_name = view[f'Tables_in_{config["db"]["db"]}']
            print(f"View: {view_name}")

            # Try to get view definition
            try:
                cursor.execute(f"SHOW CREATE VIEW `{view_name}`")
                view_def = cursor.fetchone()
                print(f"Definition:\n{view_def['Create View']}\n")
            except Exception as e:
                print(f"Error getting definition: {e}\n")

        # Drop the broken view
        print("\nDropping broken view 'ActiveLocationsWithSafety'...")
        cursor.execute("DROP VIEW IF EXISTS ActiveLocationsWithSafety")
        connection.commit()
        print("[OK] View dropped successfully\n")

finally:
    connection.close()
    print("[SUCCESS] Database connection closed.")
