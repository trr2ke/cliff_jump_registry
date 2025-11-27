
from pathlib import Path
import pymysql
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

    def verify_new(self):
        self.errors = []

        # Required field: location_id (parent location)
        if 'location_id' not in self.data[0] or len(str(self.data[0]['location_id']).strip()) == 0:
            self.errors.append('Parent location is required.')
        else:
            try:
                loc_id = int(self.data[0]['location_id'])
                if loc_id <= 0:
                    self.errors.append('Invalid parent location.')
            except ValueError:
                self.errors.append('Invalid parent location.')

        # Required field: name
        if 'name' not in self.data[0] or len(self.data[0]['name'].strip()) == 0:
            self.errors.append('Jump point name cannot be blank.')

        # Optional field: height_feet (if provided, must be positive number)
        if 'height_feet' in self.data[0] and self.data[0]['height_feet'] is not None and len(str(self.data[0]['height_feet']).strip()) > 0:
            try:
                height = float(self.data[0]['height_feet'])
                if height <= 0:
                    self.errors.append('Height must be a positive number.')
            except ValueError:
                self.errors.append('Height must be a valid number.')

        # Optional field: difficulty (if provided, must be in allowed list)
        if 'difficulty' in self.data[0] and self.data[0]['difficulty'] is not None and len(str(self.data[0]['difficulty']).strip()) > 0:
            if self.data[0]['difficulty'] not in self.difficulty_list():
                self.errors.append(f"Difficulty must be one of {self.difficulty_list()}")

        # Auto-set fields
        self.data[0]['submission_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data[0]['verified'] = 0  # 0 = FALSE in MySQL TINYINT

        if len(self.errors) == 0:
            return True
        else:
            return False

    def verify_update(self):
        self.errors = []

        # Same validations as verify_new, but don't reset created_date or submitted_by
        if 'location_id' not in self.data[0] or len(str(self.data[0]['location_id']).strip()) == 0:
            self.errors.append('Parent location is required.')
        else:
            try:
                loc_id = int(self.data[0]['location_id'])
                if loc_id <= 0:
                    self.errors.append('Invalid parent location.')
            except ValueError:
                self.errors.append('Invalid parent location.')

        if 'name' not in self.data[0] or len(self.data[0]['name'].strip()) == 0:
            self.errors.append('Jump point name cannot be blank.')

        if 'height_feet' in self.data[0] and self.data[0]['height_feet'] is not None and len(str(self.data[0]['height_feet']).strip()) > 0:
            try:
                height = float(self.data[0]['height_feet'])
                if height <= 0:
                    self.errors.append('Height must be a positive number.')
            except ValueError:
                self.errors.append('Height must be a valid number.')

        if 'difficulty' in self.data[0] and self.data[0]['difficulty'] is not None and len(str(self.data[0]['difficulty']).strip()) > 0:
            if self.data[0]['difficulty'] not in self.difficulty_list():
                self.errors.append(f"Difficulty must be one of {self.difficulty_list()}")

        if len(self.errors) == 0:
            return True
        else:
            return False

    def get_by_location(self, location_id):
        """Get all jump points for a specific location"""
        self.data = []
        sql = f"SELECT * FROM `{self.tn}` WHERE `location_id` = %s ORDER BY `height_feet` DESC"
        self.cur.execute(sql, [location_id])
        for row in self.cur:
            self.data.append(row)
        return self.data
