"""
User Model Test Script
======================

Tests CRUD operations and validation for the user model.
This script is used for development and testing purposes.
"""

import yaml
from pathlib import Path
import pymysql
import datetime
from user import user

# Initialize and truncate user table for clean test
u = user()
u.truncate()

# Test 1: Insert new user
d = {'username': 'Tyler', 'email': 'tconlon@clarkson.edu', 'user_type': 'admin', 'password': '123', 'password2': '123'}
u.set(d)
if u.verify_new():
    u.insert()
    print(f"ID {u.data[0][u.pk]} inserted")
else:
    print(u.errors)

# Test 2: Delete user
u.deleteById(u.data[0][u.pk])

u = user()
u.getAll()
print(f"len of u.data is {len(u.data)} after delete.")

# Test 3: Truncate and re-insert
u = user()
u.truncate()

d = {'username': 'Tyler', 'email': 'tconlon@clarkson.edu', 'user_type': 'admin', 'password': '123', 'password2': '123'}
u.set(d)
if u.verify_new():
    u.insert()
    print(f"ID {u.data[0][u.pk]} inserted")
else:
    print(u.errors)


# Test 4: Update user
u = user()
u.getByField('email', 'tconlon@clarkson.edu')
u.data[0]['username'] = 'newName'
if u.verify_update():
    u.update()
    print(f"ID {u.data[0][u.pk]} updated")
    u = user()
    u.getAll()
    print(f"new name is {u.data[0]['username']}")
else:
    print(u.errors)





# Test 5: Password mismatch validation
u = user()
u.getByField('email', 'tconlon@clarkson.edu')
u.data[0]['password'] = '123'
u.data[0]['password2'] = '1234'
if u.verify_update():
    u.update()
else:
    print(u.errors)

# Test 6: Invalid role validation
u = user()
u.getByField('email', 'tconlon@clarkson.edu')
u.data[0]['user_type'] = 'invalid_role'
if u.verify_update():
    u.update()
else:
    print(u.errors)

# Test 7: Duplicate email validation
d = {'username': 'Tyler', 'email': 'tconlon@clarkson.edu', 'user_type': 'admin', 'password': '123', 'password2': '123'}
u.set(d)
if u.verify_new():
    u.insert()
    print(f"ID {u.data[0][u.pk]} inserted")
else:
    print(u.errors)


# Test 8: Login with correct credentials
u = user()
if u.tryLogin('tconlon@clarkson.edu', '123'):
    print(f"user with email {u.data[0]['email']} logged in")
else:
    print('login failed')

# Test 9: Login with username instead of email
u = user()
if u.tryLogin('Tyler', '123'):
    print(f"user with username {u.data[0]['username']} logged in")
else:
    print('login failed')

# Test 10: Change password
u = user()
u.getByField('email', 'tconlon@clarkson.edu')
u.data[0]['password'] = '1234'
u.data[0]['password2'] = '1234'
if u.verify_update():
    u.update()
    print("Password updated successfully")
else:
    print(u.errors)

# Test 11: Login with new password
u = user()
if u.tryLogin('tconlon@clarkson.edu', '1234'):
    print(f"user with email {u.data[0]['email']} logged in with new password")
else:
    print('login failed')

# Test 12: Login with incorrect password
u = user()
if u.tryLogin('tconlon@clarkson.edu', '123456'):
    print(f"user with email {u.data[0]['email']} logged in")
else:
    print('login failed (expected - wrong password)')