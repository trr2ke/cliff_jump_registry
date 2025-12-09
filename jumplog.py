"""
JumpLog Model
Manages personal jump diary entries for users to track their cliff jumping history.
"""

import datetime
from baseObject import baseObject

class jumplog(baseObject):
    def __init__(self):
        self.setup()

    def _validate_user_id(self, user_id):
        """Helper to validate user_id. Returns error message or None."""
        if user_id is None or len(str(user_id).strip()) == 0:
            return 'User is required.'
        try:
            uid = int(user_id)
            if uid <= 0:
                return 'Invalid user.'
        except ValueError:
            return 'Invalid user.'
        return None

    def _validate_location_id(self, location_id):
        """Helper to validate location_id. Returns error message or None."""
        if location_id is None or len(str(location_id).strip()) == 0:
            return 'Location is required.'
        try:
            lid = int(location_id)
            if lid <= 0:
                return 'Invalid location.'
        except ValueError:
            return 'Invalid location.'
        return None

    def _validate_jump_date(self, jump_date):
        """Helper to validate jump_date. Returns error message or None."""
        if jump_date is None or len(str(jump_date).strip()) == 0:
            return 'Jump date is required.'
        return None

    def verify_new(self):
        self.errors = []

        # Validate user_id
        error = self._validate_user_id(self.data[0].get('user_id'))
        if error:
            self.errors.append(error)

        # Validate location_id
        error = self._validate_location_id(self.data[0].get('location_id'))
        if error:
            self.errors.append(error)

        # Validate jump_date
        error = self._validate_jump_date(self.data[0].get('jump_date'))
        if error:
            self.errors.append(error)

        # Auto-set timestamp
        if 'jump_timestamp' not in self.data[0] or not self.data[0]['jump_timestamp']:
            self.data[0]['jump_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Default is_private to 0 if not set
        if 'is_private' not in self.data[0] or self.data[0]['is_private'] == '':
            self.data[0]['is_private'] = 0

        return len(self.errors) == 0

    def verify_update(self):
        self.errors = []

        # Same validations as verify_new
        error = self._validate_user_id(self.data[0].get('user_id'))
        if error:
            self.errors.append(error)

        error = self._validate_location_id(self.data[0].get('location_id'))
        if error:
            self.errors.append(error)

        error = self._validate_jump_date(self.data[0].get('jump_date'))
        if error:
            self.errors.append(error)

        return len(self.errors) == 0

    def get_by_user(self, user_id):
        """Get all jump logs for a specific user"""
        self.data = []
        sql = f"""
            SELECT jl.*, l.name as location_name
            FROM `{self.tn}` jl
            LEFT JOIN Locations l ON jl.location_id = l.location_id
            WHERE jl.user_id = %s
            ORDER BY jl.jump_date DESC
        """
        self.cur.execute(sql, [user_id])
        for row in self.cur:
            self.data.append(row)
        return self.data

    def get_public_logs(self, limit=50):
        """Get recent public jump logs for community feed"""
        self.data = []
        sql = f"""
            SELECT jl.*, l.name as location_name, u.username
            FROM `{self.tn}` jl
            LEFT JOIN Locations l ON jl.location_id = l.location_id
            LEFT JOIN Users u ON jl.user_id = u.user_id
            WHERE jl.is_private = 0
            ORDER BY jl.jump_timestamp DESC
            LIMIT %s
        """
        self.cur.execute(sql, [limit])
        for row in self.cur:
            self.data.append(row)
        return self.data
