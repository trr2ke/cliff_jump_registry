"""
Location Model
==============

Manages cliff jumping locations with GPS coordinates and flagging system.

Each location represents a general cliff jumping area that can contain
multiple jump points (specific spots to jump from).
"""

from baseObject import baseObject

class location(baseObject):
    def __init__(self):
        """Initialize location object."""
        self.setup()

    def _validate_latitude(self, lat_value):
        """
        Validate latitude coordinate.

        Args:
            lat_value: Latitude value to validate

        Returns:
            str or None: Error message if invalid, None if valid
        """
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
        """
        Validate longitude coordinate.

        Args:
            lng_value: Longitude value to validate

        Returns:
            str or None: Error message if invalid, None if valid
        """
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
        """
        Validate location name.

        Returns:
            str or None: Error message if invalid, None if valid
        """
        if 'name' not in self.data[0] or len(self.data[0]['name'].strip()) == 0:
            return 'Location name cannot be blank.'
        return None

    def verify_new(self):
        """
        Validate data for creating a new location.

        Validates:
        - Location name is not blank
        - Latitude is valid (-90 to 90)
        - Longitude is valid (-180 to 180)

        Auto-sets flag_count to 0 for new locations.

        Returns:
            bool: True if validation passes, False otherwise
        """
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

        # Auto-set flag_count default
        if 'flag_count' not in self.data[0]:
            self.data[0]['flag_count'] = 0

        return len(self.errors) == 0

    def verify_update(self):
        """
        Validate data for updating an existing location.

        Same validations as verify_new.
        Does not reset submission_timestamp or submitted_by fields.

        Returns:
            bool: True if validation passes, False otherwise
        """
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

        return len(self.errors) == 0
