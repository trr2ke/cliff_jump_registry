import yaml
from pathlib import Path
import pymysql
import datetime
from user import user


'''
TODO:
x- add verify user role
x- truncate() for testing
x- test insert()
x- test deleteById()
x- test update()
- test verify new/update:
    - email in use
    - password len
    - passwords match
    - user role
- test tryLogin()




'''

u = user()
u.truncate()


d = {'name':'Tyler','email':'tconlon@clarkson.edu','role':'admin','password':'123','password2':'123'}
u.set(d)
if u.verify_new():
    u.insert()
    print(f"ID {u.data[0][u.pk]} inserted")
else:
    print(u.errors)


u.deleteById(u.data[0][u.pk])

u = user()
u.getAll()
print(f"len of u.data is {len(u.data)} after delete.")



u = user()
u.truncate()


d = {'name':'Tyler','email':'tconlon@clarkson.edu','role':'admin','password':'123','password2':'123'}
u.set(d)
if u.verify_new():
    u.insert()
    print(f"ID {u.data[0][u.pk]} inserted")
else:
    print(u.errors)


u = user()
u.getByField('email','tconlon@clarkson.edu')
u.data[0]['name'] = 'newName'
if u.verify_update():
    u.update()
    print(f"ID {u.data[0][u.pk]} updated")
    u = user()
    u.getAll()
    print(f"new name is {u.data[0]['name']}")
else:
    print(u.errors)





u = user()
u.getByField('email','tconlon@clarkson.edu')
u.data[0]['password'] = '123'
u.data[0]['password2'] = '1234'
if u.verify_update():
    u.update()
else:
    print(u.errors)

u = user()
u.getByField('email','tconlon@clarkson.edu')
u.data[0]['role'] = '123'
if u.verify_update():
    u.update()
else:
    print(u.errors)



d = {'name':'Tyler','email':'tconlon@clarkson.edu','role':'admin','password':'123','password2':'123'}
u.set(d)
if u.verify_new():
    u.insert()
    print(f"ID {u.data[0][u.pk]} inserted")
else:
    print(u.errors)


u = user()
if u.tryLogin('tconlon@clarkson.edu','123'):
    print(f"user with email {u.data[0]['email']} logged in")
else:
    print('login failed')

u = user()
if u.tryLogin('tconlon@clarkson.edu','123'):
    print(f"user with email {u.data[0]['email']} logged in")
else:
    print('login failed')


u = user()
u.getByField('email','tconlon@clarkson.edu')
print(u.data[0]['password'])
u.data[0]['password'] = '1234'
u.data[0]['password2'] = '1234'
if u.verify_update():
    
    u.update()
    print(u.data[0]['password'])
else:
    print(u.errors)

u = user()
if u.tryLogin('tconlon@clarkson.edu','1234'):
    print(f"user with email {u.data[0]['email']} logged in")
else:
    print('login failed')

u = user()
if u.tryLogin('tconlon@clarkson.edu','123456'):
    print(f"user with email {u.data[0]['email']} logged in")
else:
    print('login failed')