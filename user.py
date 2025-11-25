
from pathlib import Path
import pymysql
import datetime
from baseObject import baseObject
import hashlib

class user(baseObject):
    def __init__(self):
        self.setup()
        self.roles = [{'value':'admin','text':'Admin'},{'value':'trusted','text':'Trusted'},{'value':'registered','text':'Registered'},{'value':'guest','text':'Guest'}]
    def hashPassword(self,pw):
        pw = pw+'xyz'
        return hashlib.md5(pw.encode('utf-8')).hexdigest()
    def role_list(self):
        rl = []
        for item in self.roles:
            rl.append(item['value'])
        return rl
    def verify_new(self):
        self.errors = []
        #
        if 'username' not in self.data[0] or len(self.data[0]['username'].strip()) == 0:
            self.errors.append('Username cannot be blank.')
        if '@' not in self.data[0]['email']:
            self.errors.append('Email must contain @')
        u = user()
        u.getByField('email',self.data[0]['email'])
        if len(u.data) > 0:
            self.errors.append(f"Email address is already in use. ({self.data[0]['email']})")
        
        if len(self.data[0]['password']) < 3:
            self.errors.append('Password should be greater than 3 chars.')
        if self.data[0]['password'] != self.data[0]['password2']:
            self.errors.append('Retyped password must match.')
        self.data[0]['password_hash'] = self.hashPassword(self.data[0]['password'])
        del self.data[0]['password']
        del self.data[0]['password2']
        if self.data[0]['user_type'] not in self.role_list():
            self.errors.append(f"Role must be one of {self.role_list()}")
        #
       
        
        if len(self.errors) == 0:
            return True
        else:
            return False
    def verify_update(self):
        self.errors = []
        #
        if 'username' not in self.data[0] or len(self.data[0]['username'].strip()) == 0:
            self.errors.append('Username cannot be blank.')
        if '@' not in self.data[0]['email']:
            self.errors.append('Email must contain @')
        u = user()
        u.getByField('email',self.data[0]['email'])
        if len(u.data) > 0 and u.data[0][u.pk] != self.data[0][self.pk]:
            self.errors.append(f"Email address is already in use. ({self.data[0]['email']})")
        
        if 'password2' in self.data[0].keys() and len(self.data[0]['password2']) > 0:
            if len(self.data[0]['password']) < 3:
                self.errors.append('Password should be greater than 3 chars.')
            if self.data[0]['password'] != self.data[0]['password2']:
                self.errors.append('Retyped password must match.')

            self.data[0]['password_hash'] = self.hashPassword(self.data[0]['password'])
            del self.data[0]['password']
            del self.data[0]['password2']
        else:
            del self.data[0]['password']
            if 'password2' in self.data[0].keys():
                del self.data[0]['password2']
        if self.data[0]['user_type'] not in self.role_list():
            self.errors.append(f"Role must be one of {self.role_list()}")
        #
        
        
        if len(self.errors) == 0:
            return True
        else:
            return False
    
    def tryLogin(self,un, pw):
        #print(un,pw)
        pw = self.hashPassword(pw)
        #print(un,pw)
        self.data = []
        sql = f'''SELECT * FROM `{self.tn}` WHERE (`email` = %s OR `username` = %s) AND `password_hash` = %s;'''
        #print(sql,[un,pw])
        self.cur.execute(sql,[un,un,pw])
        for row in self.cur:
            self.data.append(row)
        if len(self.data) == 1:
            return True
        return False
            