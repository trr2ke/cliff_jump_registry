
import datetime
from baseObject import baseObject

class jumppoint(baseObject):
    def __init__(self):
        self.setup()
        self.difficulty_levels = [
            {'value':'beginner','text':'Beginner'},
            {'value':'intermediate','text':'Intermediate'},
            {'value':'advanced','text':'Advanced'},
            {'value':'expert','text':'Expert'}
        ]

    def difficulty_list(self):
        dl = []
        for item in self.difficulty_levels:
            dl.append(item['value'])
        return dl

    def _validate_location_id(self, loc_id):
        """Helper to validate location_id. Returns error message or None."""
        if loc_id is None or len(str(loc_id).strip()) == 0:
            return 'Parent location is required.'
        try:
            location_id = int(loc_id)
            if location_id <= 0:
                return 'Invalid parent location.'
        except ValueError:
            return 'Invalid parent location.'
        return None

    def _validate_name(self):
        """Helper to validate jump point name. Returns error message or None."""
        if 'name' not in self.data[0] or len(self.data[0]['name'].strip()) == 0:
            return 'Jump point name cannot be blank.'
        return None

    def _validate_height(self, height_value):
        """Helper to validate height_feet. Returns error message or None."""
        if height_value is not None and len(str(height_value).strip()) > 0:
            try:
                height = float(height_value)
                if height <= 0:
                    return 'Height must be a positive number.'
            except ValueError:
                return 'Height must be a valid number.'
        return None

    def _validate_difficulty(self, difficulty_value):
        """Helper to validate difficulty. Returns error message or None."""
        if difficulty_value is not None and len(str(difficulty_value).strip()) > 0:
            if difficulty_value not in self.difficulty_list():
                return f"Difficulty must be one of {self.difficulty_list()}"
        return None

    def verify_new(self):
        self.errors = []

        # Validate location_id
        error = self._validate_location_id(self.data[0].get('location_id'))
        if error:
            self.errors.append(error)

        # Validate name
        error = self._validate_name()
        if error:
            self.errors.append(error)

        # Validate height (optional)
        error = self._validate_height(self.data[0].get('height_feet'))
        if error:
            self.errors.append(error)

        # Validate difficulty (optional)
        error = self._validate_difficulty(self.data[0].get('difficulty'))
        if error:
            self.errors.append(error)

        # Auto-set fields
        self.data[0]['submission_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data[0]['verified'] = 0  # 0 = FALSE in MySQL TINYINT

        return len(self.errors) == 0

    def verify_update(self):
        self.errors = []

        # Same validations as verify_new, but don't reset created_date or submitted_by
        error = self._validate_location_id(self.data[0].get('location_id'))
        if error:
            self.errors.append(error)

        error = self._validate_name()
        if error:
            self.errors.append(error)

        error = self._validate_height(self.data[0].get('height_feet'))
        if error:
            self.errors.append(error)

        error = self._validate_difficulty(self.data[0].get('difficulty'))
        if error:
            self.errors.append(error)

        return len(self.errors) == 0

    def get_by_location(self, location_id):
        """Get all jump points for a specific location"""
        self.data = []
        sql = f"SELECT * FROM `{self.tn}` WHERE `location_id` = %s ORDER BY `height_feet` DESC"
        self.cur.execute(sql, [location_id])
        for row in self.cur:
            self.data.append(row)
        return self.data
