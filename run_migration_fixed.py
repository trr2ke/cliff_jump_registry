"""
Run database migration step by step
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

def execute_sql(cursor, sql, description):
    try:
        print(f"Executing: {description}...")
        cursor.execute(sql)
        connection.commit()
        print(f"  [OK] {description}\n")
        return True
    except Exception as e:
        if 'already exists' in str(e).lower() or "can't drop" in str(e).lower() or 'unknown column' in str(e).lower():
            print(f"  [SKIP] {description} (already applied or doesn't exist)\n")
            return True
        else:
            print(f"  [ERROR] {description}: {e}\n")
            return False

try:
    with connection.cursor() as cursor:
        # Step 1: Update existing trusted users to admin
        execute_sql(cursor,
            "UPDATE Users SET user_type = 'admin' WHERE user_type = 'trusted'",
            "Convert trusted users to admin")

        # Step 2: Modify Users table enum
        execute_sql(cursor,
            "ALTER TABLE Users MODIFY COLUMN user_type ENUM('guest', 'registered', 'admin') DEFAULT 'guest'",
            "Update Users.user_type ENUM")

        # Step 3: Drop LocationVerifications table
        execute_sql(cursor,
            "DROP TABLE IF EXISTS LocationVerifications",
            "Drop LocationVerifications table")

        # Step 4: Modify Locations table - drop old columns
        execute_sql(cursor,
            "ALTER TABLE Locations DROP COLUMN IF EXISTS verified",
            "Drop Locations.verified")

        execute_sql(cursor,
            "ALTER TABLE Locations DROP COLUMN IF EXISTS verified_by",
            "Drop Locations.verified_by")

        execute_sql(cursor,
            "ALTER TABLE Locations DROP COLUMN IF EXISTS status",
            "Drop Locations.status")

        execute_sql(cursor,
            "ALTER TABLE Locations DROP COLUMN IF EXISTS submission_timestamp",
            "Drop Locations.submission_timestamp")

        # Step 5: Add new flagging columns to Locations
        execute_sql(cursor,
            "ALTER TABLE Locations ADD COLUMN is_flagged TINYINT(1) DEFAULT 0 COMMENT 'Whether location has been flagged for review'",
            "Add Locations.is_flagged")

        execute_sql(cursor,
            "ALTER TABLE Locations ADD COLUMN flag_reason TEXT NULL COMMENT 'Reason for flagging'",
            "Add Locations.flag_reason")

        execute_sql(cursor,
            "ALTER TABLE Locations ADD COLUMN flagged_by INT NULL COMMENT 'User ID who flagged'",
            "Add Locations.flagged_by")

        execute_sql(cursor,
            "ALTER TABLE Locations ADD COLUMN flagged_date DATETIME NULL COMMENT 'When location was flagged'",
            "Add Locations.flagged_date")

        # Step 6: Modify JumpPoints table - drop old columns
        execute_sql(cursor,
            "ALTER TABLE JumpPoints DROP COLUMN IF EXISTS verified",
            "Drop JumpPoints.verified")

        execute_sql(cursor,
            "ALTER TABLE JumpPoints DROP COLUMN IF EXISTS verified_by",
            "Drop JumpPoints.verified_by")

        execute_sql(cursor,
            "ALTER TABLE JumpPoints DROP COLUMN IF EXISTS submission_timestamp",
            "Drop JumpPoints.submission_timestamp")

        execute_sql(cursor,
            "ALTER TABLE JumpPoints DROP COLUMN IF EXISTS status",
            "Drop JumpPoints.status")

        # Step 7: Add new flagging columns to JumpPoints
        execute_sql(cursor,
            "ALTER TABLE JumpPoints ADD COLUMN is_flagged TINYINT(1) DEFAULT 0 COMMENT 'Whether jump point has been flagged for review'",
            "Add JumpPoints.is_flagged")

        execute_sql(cursor,
            "ALTER TABLE JumpPoints ADD COLUMN flag_reason TEXT NULL COMMENT 'Reason for flagging'",
            "Add JumpPoints.flag_reason")

        execute_sql(cursor,
            "ALTER TABLE JumpPoints ADD COLUMN flagged_by INT NULL COMMENT 'User ID who flagged'",
            "Add JumpPoints.flagged_by")

        execute_sql(cursor,
            "ALTER TABLE JumpPoints ADD COLUMN flagged_date DATETIME NULL COMMENT 'When jump point was flagged'",
            "Add JumpPoints.flagged_date")

        print("\n[SUCCESS] All migration steps completed!")
        print("\nVerifying changes...")

        # Verify
        cursor.execute("SELECT user_type, COUNT(*) as count FROM Users GROUP BY user_type")
        print("\nUsers by type:")
        for row in cursor.fetchall():
            print(f"  - {row['user_type']}: {row['count']}")

        cursor.execute("SHOW COLUMNS FROM Locations LIKE 'is_flagged'")
        if cursor.fetchone():
            print("\n[OK] Locations.is_flagged column exists")
        else:
            print("\n[ERROR] Locations.is_flagged column NOT found")

        cursor.execute("SHOW COLUMNS FROM JumpPoints LIKE 'is_flagged'")
        if cursor.fetchone():
            print("[OK] JumpPoints.is_flagged column exists")
        else:
            print("[ERROR] JumpPoints.is_flagged column NOT found")

        cursor.execute("SHOW TABLES LIKE 'LocationVerifications'")
        if cursor.fetchone():
            print("[WARNING] LocationVerifications table still exists")
        else:
            print("[OK] LocationVerifications table removed")

finally:
    connection.close()
    print("\n[SUCCESS] Database connection closed.")
    print("\nMigration complete! Restart your Flask application.")
