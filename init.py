"""
Database Initialization Script
==============================

Creates initial admin user for the Cliff Jump Registry application.

USAGE: Run this script manually to set up the first admin account:
    python init.py

WARNING: This script truncates the Users table, deleting all existing users.
Only run this when setting up a fresh database.
"""

from user import user

# Initialize user object and clear existing data
u = user()
u.truncate()

# Create default admin user
d = {
    'username': 'admin',
    'email': 'admin@example.com',
    'user_type': 'admin',
    'password': 'changeme123',
    'password2': 'changeme123'
}
u.set(d)
if u.verify_new():
    u.insert()
    print(f"Admin user created: {d['username']} / {d['email']}")
    print(f"Default password: {d['password']}")
    print("IMPORTANT: Change this password immediately after first login!")
else:
    print("Error creating admin user:")
    print(u.errors)