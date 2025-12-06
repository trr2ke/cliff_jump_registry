
import datetime
from baseObject import baseObject

class location(baseObject):
    def __init__(self):
        self.setup()

    def _validate_latitude(self, lat_value):
        """Helper to validate latitude. Returns error message or None."""
        if lat_value is None or len(str(lat_value).strip()) == 0:
            return 'Latitude is required.'
        try:
            lat = float(lat_value)
            if lat < -90 or lat > 90:
                return 'Latitude must be between -90 and 90.'
        except ValueError:
            return 'Latitude must be a valid number.'
        return None

    def _validate_longitude(self, lng_value):
        """Helper to validate longitude. Returns error message or None."""
        if lng_value is None or len(str(lng_value).strip()) == 0:
            return 'Longitude is required.'
        try:
            lng = float(lng_value)
            if lng < -180 or lng > 180:
                return 'Longitude must be between -180 and 180.'
        except ValueError:
            return 'Longitude must be a valid number.'
        return None

    def _validate_name(self):
        """Helper to validate location name. Returns error message or None."""
        if 'name' not in self.data[0] or len(self.data[0]['name'].strip()) == 0:
            return 'Location name cannot be blank.'
        return None

    def verify_new(self):
        self.errors = []

        # Validate name
        error = self._validate_name()
        if error:
            self.errors.append(error)

        # Validate latitude
        error = self._validate_latitude(self.data[0].get('latitude'))
        if error:
            self.errors.append(error)

        # Validate longitude
        error = self._validate_longitude(self.data[0].get('longitude'))
        if error:
            self.errors.append(error)

        # Auto-set fields
        self.data[0]['submission_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data[0]['verified'] = 0  # 0 = FALSE in MySQL TINYINT

        return len(self.errors) == 0

    def verify_update(self):
        self.errors = []

        # Same validations as verify_new, but don't reset submission_timestamp or submitted_by
        error = self._validate_name()
        if error:
            self.errors.append(error)

        error = self._validate_latitude(self.data[0].get('latitude'))
        if error:
            self.errors.append(error)

        error = self._validate_longitude(self.data[0].get('longitude'))
        if error:
            self.errors.append(error)

        return len(self.errors) == 0
