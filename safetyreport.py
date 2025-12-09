"""
SafetyReport Model
Manages real-time safety condition reports for cliff jump locations.
"""

import datetime
from baseObject import baseObject

class safetyreport(baseObject):
    def __init__(self):
        self.setup()

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

    def _validate_report_date(self, report_date):
        """Helper to validate report_date. Returns error message or None."""
        if report_date is None or len(str(report_date).strip()) == 0:
            return 'Report date is required.'
        return None

    def _validate_conditions(self, conditions):
        """Helper to validate conditions. Returns error message or None."""
        if conditions is None or len(str(conditions).strip()) == 0:
            return 'Conditions description is required.'
        return None

    def _validate_is_safe(self, is_safe):
        """Helper to validate is_safe flag. Returns error message or None."""
        if is_safe is None or str(is_safe).strip() == '':
            return 'Safety status is required.'
        return None

    def verify_new(self):
        self.errors = []

        # Validate location_id
        error = self._validate_location_id(self.data[0].get('location_id'))
        if error:
            self.errors.append(error)

        # Validate user_id
        error = self._validate_user_id(self.data[0].get('user_id'))
        if error:
            self.errors.append(error)

        # Validate report_date
        error = self._validate_report_date(self.data[0].get('report_date'))
        if error:
            self.errors.append(error)

        # Validate conditions
        error = self._validate_conditions(self.data[0].get('conditions'))
        if error:
            self.errors.append(error)

        # Validate is_safe
        error = self._validate_is_safe(self.data[0].get('is_safe'))
        if error:
            self.errors.append(error)

        # Auto-set timestamp
        if 'report_timestamp' not in self.data[0] or not self.data[0]['report_timestamp']:
            self.data[0]['report_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return len(self.errors) == 0

    def verify_update(self):
        self.errors = []

        # Same validations as verify_new
        error = self._validate_location_id(self.data[0].get('location_id'))
        if error:
            self.errors.append(error)

        error = self._validate_user_id(self.data[0].get('user_id'))
        if error:
            self.errors.append(error)

        error = self._validate_report_date(self.data[0].get('report_date'))
        if error:
            self.errors.append(error)

        error = self._validate_conditions(self.data[0].get('conditions'))
        if error:
            self.errors.append(error)

        error = self._validate_is_safe(self.data[0].get('is_safe'))
        if error:
            self.errors.append(error)

        return len(self.errors) == 0

    def get_by_location(self, location_id, limit=10):
        """Get recent safety reports for a specific location"""
        self.data = []
        sql = f"""
            SELECT sr.*, u.username
            FROM `{self.tn}` sr
            LEFT JOIN Users u ON sr.user_id = u.user_id
            WHERE sr.location_id = %s
            ORDER BY sr.report_date DESC, sr.report_timestamp DESC
            LIMIT %s
        """
        self.cur.execute(sql, [location_id, limit])
        for row in self.cur:
            self.data.append(row)
        return self.data

    def get_latest_by_location(self, location_id):
        """Get the most recent safety report for a location"""
        self.data = []
        sql = f"""
            SELECT sr.*, u.username
            FROM `{self.tn}` sr
            LEFT JOIN Users u ON sr.user_id = u.user_id
            WHERE sr.location_id = %s
            ORDER BY sr.report_date DESC, sr.report_timestamp DESC
            LIMIT 1
        """
        self.cur.execute(sql, [location_id])
        for row in self.cur:
            self.data.append(row)
        return self.data

    def get_recent_unsafe_reports(self, days=7):
        """Get recent unsafe reports across all locations"""
        self.data = []
        sql = f"""
            SELECT sr.*, l.name as location_name, u.username
            FROM `{self.tn}` sr
            LEFT JOIN Locations l ON sr.location_id = l.location_id
            LEFT JOIN Users u ON sr.user_id = u.user_id
            WHERE sr.is_safe = 0
            AND sr.report_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            ORDER BY sr.report_date DESC
        """
        self.cur.execute(sql, [days])
        for row in self.cur:
            self.data.append(row)
        return self.data
