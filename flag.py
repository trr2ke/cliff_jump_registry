"""
Flag Model
==========

Manages user-reported flags on content (locations, jumppoints, reviews, safety reports).

Supports community moderation by allowing multiple users to flag the same content
and tracking resolution by administrators.
"""

from baseObject import baseObject
import datetime

class flag(baseObject):
    def __init__(self):
        """Initialize flag object and define valid categories and types."""
        self.setup()
        self.categories = [
            {'value': 'inaccurate', 'text': 'Inaccurate Information'},
            {'value': 'dangerous', 'text': 'Dangerous/Unsafe'},
            {'value': 'inappropriate', 'text': 'Inappropriate Content'},
            {'value': 'spam', 'text': 'Spam'},
            {'value': 'outdated', 'text': 'Outdated Information'},
            {'value': 'other', 'text': 'Other'}
        ]
        self.flaggable_types = ['location', 'jumppoint', 'review', 'safetyreport']

    def category_list(self):
        """
        Get list of valid flag category values.

        Returns:
            list: List of category strings
        """
        return [item['value'] for item in self.categories]

    def _validate_flaggable_type(self, flaggable_type):
        """
        Validate flaggable_type.

        Args:
            flaggable_type (str): Type of content being flagged

        Returns:
            str or None: Error message if invalid, None if valid
        """
        if not flaggable_type or flaggable_type not in self.flaggable_types:
            return f"Flaggable type must be one of {self.flaggable_types}"
        return None

    def _validate_flaggable_id(self, flaggable_id):
        """
        Validate flaggable_id.

        Args:
            flaggable_id: ID of the content being flagged

        Returns:
            str or None: Error message if invalid, None if valid
        """
        if flaggable_id is None or str(flaggable_id).strip() == '':
            return 'Content ID is required.'
        try:
            fid = int(flaggable_id)
            if fid <= 0:
                return 'Invalid content ID.'
        except ValueError:
            return 'Invalid content ID.'
        return None

    def _validate_user_id(self, user_id):
        """
        Validate user_id.

        Args:
            user_id: ID of user creating the flag

        Returns:
            str or None: Error message if invalid, None if valid
        """
        if user_id is None or str(user_id).strip() == '':
            return 'User ID is required.'
        try:
            uid = int(user_id)
            if uid <= 0:
                return 'Invalid user ID.'
        except ValueError:
            return 'Invalid user ID.'
        return None

    def _validate_flag_reason(self, flag_reason):
        """
        Validate flag_reason.

        Args:
            flag_reason (str): Reason for flagging

        Returns:
            str or None: Error message if invalid, None if valid
        """
        if not flag_reason or len(str(flag_reason).strip()) == 0:
            return 'Please provide a reason for flagging this content.'
        if len(str(flag_reason).strip()) < 10:
            return 'Flag reason must be at least 10 characters.'
        return None

    def _validate_category(self, category):
        """
        Validate flag_category.

        Args:
            category (str): Flag category

        Returns:
            str or None: Error message if invalid, None if valid
        """
        if category and category not in self.category_list():
            return f"Flag category must be one of {self.category_list()}"
        return None

    def verify_new(self):
        """
        Validate data for creating a new flag.

        Validates:
        - flaggable_type is valid
        - flaggable_id is valid integer
        - user_id is valid integer
        - flag_reason is at least 10 characters
        - flag_category is valid (if provided)

        Auto-sets:
        - flag_date to current timestamp
        - is_resolved to 0 (not resolved)
        - flag_category to 'other' if not provided

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.errors = []

        # Validate flaggable_type
        error = self._validate_flaggable_type(self.data[0].get('flaggable_type'))
        if error:
            self.errors.append(error)

        # Validate flaggable_id
        error = self._validate_flaggable_id(self.data[0].get('flaggable_id'))
        if error:
            self.errors.append(error)

        # Validate user_id
        error = self._validate_user_id(self.data[0].get('user_id'))
        if error:
            self.errors.append(error)

        # Validate flag_reason
        error = self._validate_flag_reason(self.data[0].get('flag_reason'))
        if error:
            self.errors.append(error)

        # Validate category (optional, but if provided must be valid)
        error = self._validate_category(self.data[0].get('flag_category'))
        if error:
            self.errors.append(error)

        # Auto-set defaults
        if 'flag_date' not in self.data[0] or not self.data[0]['flag_date']:
            self.data[0]['flag_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if 'is_resolved' not in self.data[0]:
            self.data[0]['is_resolved'] = 0

        if 'flag_category' not in self.data[0] or not self.data[0]['flag_category']:
            self.data[0]['flag_category'] = 'other'

        return len(self.errors) == 0

    def verify_update(self):
        """
        Validate data for updating an existing flag (mainly for resolution).

        Returns:
            bool: True if validation passes, False otherwise
        """
        self.errors = []

        # If marking as resolved, ensure resolved_by is set
        if self.data[0].get('is_resolved') == 1:
            if not self.data[0].get('resolved_by'):
                self.errors.append('Resolved by user ID is required when marking flag as resolved.')

            # Auto-set resolved_date
            if not self.data[0].get('resolved_date'):
                self.data[0]['resolved_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return len(self.errors) == 0

    def get_by_content(self, flaggable_type, flaggable_id, include_resolved=False):
        """
        Get all flags for a specific piece of content.

        Args:
            flaggable_type (str): Type of content ('location', 'jumppoint', etc.)
            flaggable_id (int): ID of the content
            include_resolved (bool): Whether to include resolved flags

        Returns:
            list: List of flag dictionaries
        """
        self.data = []
        sql = f"""
            SELECT f.*, u.username as flagger_username, r.username as resolver_username
            FROM `{self.tn}` f
            LEFT JOIN Users u ON f.user_id = u.user_id
            LEFT JOIN Users r ON f.resolved_by = r.user_id
            WHERE f.flaggable_type = %s AND f.flaggable_id = %s
        """
        params = [flaggable_type, flaggable_id]

        if not include_resolved:
            sql += " AND f.is_resolved = 0"

        sql += " ORDER BY f.flag_date DESC"

        self.cur.execute(sql, params)
        for row in self.cur:
            self.data.append(row)
        return self.data

    def get_unresolved_flags(self, limit=50):
        """
        Get all unresolved flags across all content types.

        Args:
            limit (int): Maximum number of flags to return

        Returns:
            list: List of flag dictionaries with content details
        """
        self.data = []
        sql = f"""
            SELECT f.*, u.username as flagger_username,
                CASE
                    WHEN f.flaggable_type = 'location' THEN l.name
                    WHEN f.flaggable_type = 'jumppoint' THEN j.name
                    ELSE NULL
                END as content_name
            FROM `{self.tn}` f
            LEFT JOIN Users u ON f.user_id = u.user_id
            LEFT JOIN Locations l ON f.flaggable_type = 'location' AND f.flaggable_id = l.location_id
            LEFT JOIN JumpPoints j ON f.flaggable_type = 'jumppoint' AND f.flaggable_id = j.jump_id
            WHERE f.is_resolved = 0
            ORDER BY f.flag_date DESC
            LIMIT %s
        """
        self.cur.execute(sql, [limit])
        for row in self.cur:
            self.data.append(row)
        return self.data

    def get_by_user(self, user_id, include_resolved=False):
        """
        Get all flags created by a specific user.

        Args:
            user_id (int): ID of the user
            include_resolved (bool): Whether to include resolved flags

        Returns:
            list: List of flag dictionaries
        """
        self.data = []
        sql = f"SELECT * FROM `{self.tn}` WHERE user_id = %s"

        if not include_resolved:
            sql += " AND is_resolved = 0"

        sql += " ORDER BY flag_date DESC"

        self.cur.execute(sql, [user_id])
        for row in self.cur:
            self.data.append(row)
        return self.data

    def resolve_flag(self, flag_id, resolved_by_user_id, resolution_notes=''):
        """
        Mark a flag as resolved.

        Args:
            flag_id (int): ID of the flag to resolve
            resolved_by_user_id (int): ID of admin resolving the flag
            resolution_notes (str): Notes about the resolution

        Returns:
            bool: True if successful, False otherwise
        """
        self.getById(flag_id)
        if len(self.data) == 0:
            self.errors.append('Flag not found.')
            return False

        self.data[0]['is_resolved'] = 1
        self.data[0]['resolved_by'] = resolved_by_user_id
        self.data[0]['resolved_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data[0]['resolution_notes'] = resolution_notes

        if self.verify_update():
            self.update()
            return True
        return False
