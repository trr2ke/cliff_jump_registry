from flask import Flask
from flask import render_template
from flask import request,session, redirect, url_for, send_from_directory,make_response
from flask_session import Session
from datetime import timedelta
from user import user
import time
import yaml
from pathlib import Path

app = Flask(__name__,static_url_path='')

app.config['SECRET_KEY'] = 'sdfvbgfdjeR5y5r'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
sess = Session()
sess.init_app(app)

@app.route('/')
def home():
    return redirect('/login')

@app.context_processor
def inject_user():
    return dict(me=session.get('user'))


@app.route('/login',methods = ['GET','POST'])
def login():
    un = request.form.get('name')
    pw = request.form.get('password')
    
    if un is not None and pw is not None:
        u = user()
        if u.tryLogin(un,pw):
            print(f"login ok as {u.data[0]['email']}")
            session['user'] = u.data[0]
            session['active'] = time.time()
            return redirect('main')
        else:
            print("login failed")
            return render_template('login.html', title='Login', msg='Incorrect username or password.')
    print(un)
    m = 'Welcome back'
    return render_template('login.html', title='Login', msg=m)
@app.route('/logout',methods = ['GET','POST'])
def logout():
    if session.get('user') is not None:
        del session['user']
        del session['active']
    return render_template('login.html', title='Login', msg='You have logged out.')

@app.route('/register',methods = ['GET','POST'])
def register():
    o = user()
    action = request.args.get('action')

    if action is not None and action == 'insert':
        d = {}
        d['username'] = request.form.get('username')
        d['email'] = request.form.get('email')
        d['user_type'] = 'registered'  # Default to registered for new users
        d['password'] = request.form.get('password')
        d['password2'] = request.form.get('password2')
        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('login.html', title='Login', msg='Registration successful! Please log in.')
        else:
            return render_template('register.html',obj = o)
    else:
        o.createBlank()
        return render_template('register.html',obj = o)

@app.route('/users/manage',methods=['GET','POST'])
def manage_user():
    #if checkSession() == False: 
    #    return redirect('/login')
    o = user()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    if action is not None and action == 'delete': #action=delete&pkval=123
        o.deleteById(pkval)
        return render_template('ok_dialog.html',msg= f"Record ID {pkval} Deleted.")
    if action is not None and action == 'insert':
        d = {}
        d['username'] = request.form.get('username')
        d['email'] = request.form.get('email')
        d['user_type'] = request.form.get('user_type')
        d['password'] = request.form.get('password')
        d['password2'] = request.form.get('password2')
        o.set(d)
        if o.verify_new():
            #print(o.data)
            o.insert()
            return render_template('ok_dialog.html',msg= f"User {o.data[0][o.pk]} added.")
        else:
            return render_template('users/add.html',obj = o)
    if action is not None and action == 'update':
        o.getById(pkval)
        o.data[0]['username'] = request.form.get('username')
        o.data[0]['email'] = request.form.get('email')
        o.data[0]['user_type'] = request.form.get('user_type')
        o.data[0]['password'] = request.form.get('password')
        o.data[0]['password2'] = request.form.get('password2')
        if o.verify_update():
            o.update()
            return render_template('ok_dialog.html',msg= "User updated. ")
        else:
            return render_template('users/manage.html',obj = o)
    
    if pkval is None:
        o.getAll()
        return render_template('users/list.html',obj = o)
    if pkval == 'new':
        o.createBlank()
        return render_template('users/add.html',obj = o)
    else:
        o.getById(pkval)
        return render_template('users/manage.html',obj = o)
   

   



@app.route('/session',methods = ['GET','POST'])
def session_test():
    print(session)
    return f"{session}"
@app.route('/main')
def main():
    if checkSession() == False:
        return redirect('/login')
    print("main loaded")
    # Load config for mapbox token
    config = yaml.safe_load(Path('config.yml').read_text())
    mapbox_token = config['mapbox']['token']
    return render_template('main.html', title='Main menu', mapbox_token=mapbox_token)
# endpoint route for static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

#standalone function to be called when we need to check if a user is logged in.
def checkSession():
    if 'active' in session.keys():
        timeSinceAct = time.time() - session['active']
        #print(timeSinceAct)
        if timeSinceAct > 500:
            session['msg'] = 'Your session has timed out.'
            return False
        else:
            session['active'] = time.time()
            return True
    else:
        return False  


if __name__ == '__main__':
   app.run(host='0.0.0.0',debug=True)   