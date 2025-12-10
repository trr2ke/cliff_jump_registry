"""
Base Object Class
=================

Provides a base class for database object management with common CRUD operations.

This class handles:
- Database connection management
- Dynamic table name resolution from config.yml
- Field introspection from database schema
- Common CRUD operations (Create, Read, Update, Delete)
- Automatic primary key detection

Child classes inherit these methods and add model-specific validation and business logic.
"""

import yaml
from pathlib import Path
import pymysql

class baseObject:
    """
    Base class for database-backed objects.

    Attributes:
        fields (list): List of database field names (excluding primary key)
        data (list): List of dictionaries representing database rows
        pk (str): Primary key field name
        errors (list): Validation error messages
        config (dict): Configuration from config.yml
        tn (str): Table name for this object
        conn: Database connection object
        cur: Database cursor object
    """
    def setup(self, config_path='config.yml'):
        """
        Initialize database connection and object properties.

        Args:
            config_path (str): Path to YAML configuration file
        """
        self.fields = []  # List of non-primary-key field names
        self.data = []  # List of row dictionaries from database
        self.pk = None  # Primary key field name
        self.errors = []  # Validation error messages
        self.config_path = config_path
        self.config = yaml.safe_load(Path(self.config_path).read_text())

        # Get table name from config based on class name
        self.tn = self.config['tables'][type(self).__name__]

        # Establish database connection
        self.conn = pymysql.connect(
            host=self.config['db']['host'],
            port=3306,
            user=self.config['db']['user'],
            passwd=self.config['db']['pw'],
            db=self.config['db']['db'],
            autocommit=True
        )
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        self.getFields()

    def set(self, d):
        """
        Set object data from dictionary.

        Args:
            d (dict): Dictionary of field names and values
        """
        self.data = []
        self.data.append(d)

    def getFields(self):
        """
        Introspect database table to get field names and identify primary key.

        Populates self.fields with non-primary-key columns and self.pk with primary key name.
        """
        self.fields = []
        sql = f"DESC `{self.tn}`"
        self.cur.execute(sql)

        for row in self.cur:
            # Auto-increment field is the primary key
            if row['Extra'] == 'auto_increment':
                self.pk = row['Field']
            else:
                self.fields.append(row['Field'])

    def insert(self, n=0):
        """
        Insert a new record into the database.

        Builds parameterized INSERT query from self.data fields.
        Updates self.data with the new record's auto-generated primary key.

        Args:
            n (int): Index in self.data list (default 0)
        """
        sql = f'INSERT INTO `{self.tn}` ('
        vals = ''
        tokens = []

        # Build field list and value placeholders
        for field in self.fields:
            if field in self.data[n].keys():
                tokens.append(self.data[n][field])
                sql += f'`{field}`,' + ' '
                vals += '%s, '

        # Remove trailing commas
        sql = sql[0:-2]
        vals = vals[0:-2]

        # Complete SQL statement
        sql += ') VALUES '
        sql += f'({vals});'

        self.cur.execute(sql, tokens)
        self.data[n][self.pk] = self.cur.lastrowid  # Store auto-generated ID

    def update(self, n=0):
        """
        Update an existing record in the database.

        Builds parameterized UPDATE query from self.data fields.

        Args:
            n (int): Index in self.data list (default 0)
        """
        sql = f'UPDATE `{self.tn}` SET '
        parameters = []

        # Build SET clause with field=value pairs
        for field in self.fields:
            if field in self.data[n].keys():
                sql += f'`{field}` = %s,'
                parameters.append(self.data[n][field])

        # Remove trailing comma
        sql = sql[0:-1]

        # Add WHERE clause for primary key
        sql += f' WHERE `{self.pk}` = %s;'
        parameters.append(self.data[0][self.pk])

        self.cur.execute(sql, parameters)
    
   
    def getAll(self, order=''):
        """
        Retrieve all records from the table.

        Args:
            order (str): Optional field name to sort by
        """
        self.data = []
        sql = f'''SELECT * FROM `{self.tn}`'''

        if order != '':
            sql += f' ORDER BY {order};'
        else:
            sql += ';'

        self.cur.execute(sql)
        for row in self.cur:
            self.data.append(row)

    def getById(self, id):
        """
        Retrieve a single record by primary key.

        Args:
            id: Primary key value
        """
        self.data = []
        sql = f'''SELECT * FROM `{self.tn}` WHERE `{self.pk}` = %s;'''
        self.cur.execute(sql, [id])
        for row in self.cur:
            self.data.append(row)

    def getByField(self, fieldname, value):
        """
        Retrieve records matching a specific field value.

        Args:
            fieldname (str): Name of the field to search
            value: Value to match
        """
        self.data = []
        sql = f'''SELECT * FROM `{self.tn}` WHERE `{fieldname}` = %s;'''
        self.cur.execute(sql, [value])
        for row in self.cur:
            self.data.append(row)

    def deleteById(self, id):
        """
        Delete a record by primary key.

        Args:
            id: Primary key value of record to delete
        """
        sql = f'''DELETE FROM `{self.tn}` WHERE `{self.pk}` = %s;'''
        self.cur.execute(sql, [id])

    def truncate(self):
        """Remove all records from the table (used for testing)."""
        sql = f'''TRUNCATE TABLE `{self.tn}`;'''
        self.cur.execute(sql)

    def createBlank(self):
        """
        Create a blank record template with all fields set to empty strings.

        Useful for initializing forms with empty data.
        """
        d = {}
        for field in self.fields:
            d[field] = ''
        self.set(d)