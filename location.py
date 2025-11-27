
from pathlib import Path
import pymysql
import datetime
from baseObject import baseObject

class location(baseObject):
    def __init__(self):
        self.setup()

    def verify_new(self):
        self.errors = []

        # Required field: name (area name like "Lincoln Quarry", "Lake Champlain")
        if 'name' not in self.data[0] or len(self.data[0]['name'].strip()) == 0:
            self.errors.append('Location name cannot be blank.')

        # Required field: latitude (must be valid number)
        if 'latitude' not in self.data[0] or len(str(self.data[0]['latitude']).strip()) == 0:
            self.errors.append('Latitude is required.')
        else:
            try:
                lat = float(self.data[0]['latitude'])
                if lat < -90 or lat > 90:
                    self.errors.append('Latitude must be between -90 and 90.')
            except ValueError:
                self.errors.append('Latitude must be a valid number.')

        # Required field: longitude (must be valid number)
        if 'longitude' not in self.data[0] or len(str(self.data[0]['longitude']).strip()) == 0:
            self.errors.append('Longitude is required.')
        else:
            try:
                lng = float(self.data[0]['longitude'])
                if lng < -180 or lng > 180:
                    self.errors.append('Longitude must be between -180 and 180.')
            except ValueError:
                self.errors.append('Longitude must be a valid number.')

        # Auto-set fields
        self.data[0]['submission_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data[0]['verified'] = 0  # 0 = FALSE in MySQL TINYINT

        if len(self.errors) == 0:
            return True
        else:
            return False

    def verify_update(self):
        self.errors = []

        # Same validations as verify_new, but don't reset submission_timestamp or submitted_by
        if 'name' not in self.data[0] or len(self.data[0]['name'].strip()) == 0:
            self.errors.append('Location name cannot be blank.')

        if 'latitude' not in self.data[0] or len(str(self.data[0]['latitude']).strip()) == 0:
            self.errors.append('Latitude is required.')
        else:
            try:
                lat = float(self.data[0]['latitude'])
                if lat < -90 or lat > 90:
                    self.errors.append('Latitude must be between -90 and 90.')
            except ValueError:
                self.errors.append('Latitude must be a valid number.')

        if 'longitude' not in self.data[0] or len(str(self.data[0]['longitude']).strip()) == 0:
            self.errors.append('Longitude is required.')
        else:
            try:
                lng = float(self.data[0]['longitude'])
                if lng < -180 or lng > 180:
                    self.errors.append('Longitude must be between -180 and 180.')
            except ValueError:
                self.errors.append('Longitude must be a valid number.')

        if len(self.errors) == 0:
            return True
        else:
            return False
