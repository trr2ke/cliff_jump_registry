"""
User Model
==========

Manages user accounts, authentication, and role-based permissions.

Supports three user roles:
- guest: View-only access (auto-assigned to unauthenticated users)
- registered: Can create and edit content
- admin: Full system access including user management
"""

from baseObject import baseObject
import hashlib

class user(baseObject):
    def __init__(self):
        """Initialize user object and define available user roles."""
        self.setup()
        self.roles = [
            {'value': 'admin', 'text': 'Admin'},
            {'value': 'registered', 'text': 'Registered'},
            {'value': 'guest', 'text': 'Guest'}
        ]

    def hashPassword(self, pw):
        """
        Hash password using MD5 with salt.

        Args:
            pw (str): Plain text password

        Returns:
            str: MD5 hash of password with salt
        """
        pw = pw + 'xyz'  # Add salt to password
        return hashlib.md5(pw.encode('utf-8')).hexdigest()

    def role_list(self):
        """
        Get list of valid user role values.

        Returns:
            list: List of role strings ['admin', 'registered', 'guest']
        """
        rl = []
        for item in self.roles:
            rl.append(item['value'])
        return rl

    def verify_new(self):
        """
        Validate data for creating a new user.

        Validates:
        - Username is not blank
        - Email contains @ symbol
        - Email is not already in use
        - Password is at least 3 characters
        - Password confirmation matches
        - User role is valid

        If validation passes, hashes the password and removes plaintext password fields.

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.errors = []

        # Validate username
        if 'username' not in self.data[0] or len(self.data[0]['username'].strip()) == 0:
            self.errors.append('Username cannot be blank.')

        # Validate email format
        if '@' not in self.data[0]['email']:
            self.errors.append('Email must contain @')

        # Check if email is already in use
        u = user()
        u.getByField('email', self.data[0]['email'])
        if len(u.data) > 0:
            self.errors.append(f"Email address is already in use. ({self.data[0]['email']})")

        # Validate password length
        if len(self.data[0]['password']) < 3:
            self.errors.append('Password should be greater than 3 chars.')

        # Validate password confirmation
        if self.data[0]['password'] != self.data[0]['password2']:
            self.errors.append('Retyped password must match.')

        # Hash password and remove plaintext versions
        self.data[0]['password_hash'] = self.hashPassword(self.data[0]['password'])
        del self.data[0]['password']
        del self.data[0]['password2']

        # Validate user role
        if self.data[0]['user_type'] not in self.role_list():
            self.errors.append(f"Role must be one of {self.role_list()}")

        return len(self.errors) == 0
    def verify_update(self):
        """
        Validate data for updating an existing user.

        Similar to verify_new, but:
        - Allows email reuse if it's the same user
        - Password update is optional (only validated if provided)

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.errors = []

        # Validate username
        if 'username' not in self.data[0] or len(self.data[0]['username'].strip()) == 0:
            self.errors.append('Username cannot be blank.')

        # Validate email format
        if '@' not in self.data[0]['email']:
            self.errors.append('Email must contain @')

        # Check if email is in use by a different user
        u = user()
        u.getByField('email', self.data[0]['email'])
        if len(u.data) > 0 and u.data[0][u.pk] != self.data[0][self.pk]:
            self.errors.append(f"Email address is already in use. ({self.data[0]['email']})")

        # Only validate password if user is changing it
        if 'password2' in self.data[0].keys() and len(self.data[0]['password2']) > 0:
            if len(self.data[0]['password']) < 3:
                self.errors.append('Password should be greater than 3 chars.')
            if self.data[0]['password'] != self.data[0]['password2']:
                self.errors.append('Retyped password must match.')

            # Hash new password and remove plaintext versions
            self.data[0]['password_hash'] = self.hashPassword(self.data[0]['password'])
            del self.data[0]['password']
            del self.data[0]['password2']
        else:
            # Not changing password - remove password fields
            del self.data[0]['password']
            if 'password2' in self.data[0].keys():
                del self.data[0]['password2']

        # Validate user role
        if self.data[0]['user_type'] not in self.role_list():
            self.errors.append(f"Role must be one of {self.role_list()}")

        return len(self.errors) == 0

    def tryLogin(self, un, pw):
        """
        Attempt to authenticate a user with username/email and password.

        Args:
            un (str): Username or email address
            pw (str): Plain text password

        Returns:
            bool: True if login successful, False otherwise
        """
        pw = self.hashPassword(pw)
        self.data = []

        # Check for username OR email match with matching password hash
        sql = f'''SELECT * FROM `{self.tn}` WHERE (`email` = %s OR `username` = %s) AND `password_hash` = %s;'''
        self.cur.execute(sql, [un, un, pw])

        for row in self.cur:
            self.data.append(row)

        # Login successful if exactly one user found
        if len(self.data) == 1:
            return True
        return False
            