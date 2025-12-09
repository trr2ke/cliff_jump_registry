"""
Review Model
Manages user reviews and ratings for cliff jump locations.
"""

import datetime
from baseObject import baseObject

class review(baseObject):
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

    def _validate_rating(self, rating, field_name="Rating"):
        """Helper to validate rating (1-5). Returns error message or None."""
        if rating is None or len(str(rating).strip()) == 0:
            return f'{field_name} is required.'
        try:
            r = int(rating)
            if r < 1 or r > 5:
                return f'{field_name} must be between 1 and 5.'
        except ValueError:
            return f'{field_name} must be a number.'
        return None

    def _validate_visit_date(self, visit_date):
        """Helper to validate visit_date. Returns error message or None."""
        if visit_date is None or len(str(visit_date).strip()) == 0:
            return 'Visit date is required.'
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

        # Check if user has already reviewed this location
        if self.data[0].get('user_id') and self.data[0].get('location_id'):
            sql = f"""
                SELECT review_id FROM `{self.tn}`
                WHERE user_id = %s AND location_id = %s
            """
            self.cur.execute(sql, [self.data[0]['user_id'], self.data[0]['location_id']])
            existing = self.cur.fetchone()
            if existing:
                review_id = existing['review_id']
                self.errors.append(f'You have already reviewed this location. <a href="/reviews/manage?pkval={review_id}">Click here to edit your existing review</a>.')

        # Validate overall rating
        error = self._validate_rating(self.data[0].get('rating'), "Overall rating")
        if error:
            self.errors.append(error)

        # Validate safety rating
        error = self._validate_rating(self.data[0].get('safety_rating'), "Safety rating")
        if error:
            self.errors.append(error)

        # Validate access rating
        error = self._validate_rating(self.data[0].get('access_rating'), "Access rating")
        if error:
            self.errors.append(error)

        # Validate visit date
        error = self._validate_visit_date(self.data[0].get('visit_date'))
        if error:
            self.errors.append(error)

        # Auto-set timestamps
        if 'created_date' not in self.data[0] or not self.data[0]['created_date']:
            self.data[0]['created_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return len(self.errors) == 0

    def verify_update(self):
        self.errors = []

        # Same validations except user/location can't change
        error = self._validate_rating(self.data[0].get('rating'), "Overall rating")
        if error:
            self.errors.append(error)

        error = self._validate_rating(self.data[0].get('safety_rating'), "Safety rating")
        if error:
            self.errors.append(error)

        error = self._validate_rating(self.data[0].get('access_rating'), "Access rating")
        if error:
            self.errors.append(error)

        error = self._validate_visit_date(self.data[0].get('visit_date'))
        if error:
            self.errors.append(error)

        return len(self.errors) == 0

    def get_by_location(self, location_id):
        """Get all reviews for a specific location"""
        self.data = []
        sql = f"""
            SELECT r.*, u.username
            FROM `{self.tn}` r
            LEFT JOIN Users u ON r.user_id = u.user_id
            WHERE r.location_id = %s
            ORDER BY r.created_date DESC
        """
        self.cur.execute(sql, [location_id])
        for row in self.cur:
            self.data.append(row)
        return self.data

    def get_by_user(self, user_id):
        """Get all reviews by a specific user"""
        self.data = []
        sql = f"""
            SELECT r.*, l.name as location_name
            FROM `{self.tn}` r
            LEFT JOIN Locations l ON r.location_id = l.location_id
            WHERE r.user_id = %s
            ORDER BY r.created_date DESC
        """
        self.cur.execute(sql, [user_id])
        for row in self.cur:
            self.data.append(row)
        return self.data

    def get_location_average_ratings(self, location_id):
        """Get average ratings for a location"""
        sql = f"""
            SELECT
                AVG(rating) as avg_rating,
                AVG(safety_rating) as avg_safety,
                AVG(access_rating) as avg_access,
                COUNT(*) as review_count
            FROM `{self.tn}`
            WHERE location_id = %s
        """
        self.cur.execute(sql, [location_id])
        result = self.cur.fetchone()
        return result
