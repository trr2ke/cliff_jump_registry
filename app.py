from flask import Flask
from flask import render_template
from flask import request,session, redirect, url_for, send_from_directory,make_response
from flask_session import Session
from datetime import timedelta
from user import user
from location import location
from jumppoint import jumppoint
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

def create_guest_session():
    """Create a guest session with default guest user"""
    session['user'] = {
        'user_id': 0,
        'username': 'Guest',
        'email': 'guest@example.com',
        'user_type': 'guest'
    }
    session['active'] = time.time()

@app.route('/')
def home():
    # Auto-login as guest if not already logged in
    if 'user' not in session or session.get('user') is None:
        create_guest_session()
    return redirect('/main')

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
    # Redirect to home, which will auto-login as guest
    return redirect('/')

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

@app.route('/locations/manage',methods=['GET','POST'])
def manage_location():
    if checkSession() == False:
        return redirect('/login')

    o = location()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    user_type = session.get('user', {}).get('user_type', 'guest')

    # LIST all locations (guests can view)
    if pkval is None and action is None:
        o.getAll('name')
        return render_template('locations/list.html', obj=o)

    # Check permissions for add/edit/delete: only registered, trusted, and admin
    if user_type == 'guest':
        return render_template('ok_dialog.html', msg="Guests cannot modify locations. Please login or register to contribute.")

    # DELETE action
    if action is not None and action == 'delete':
        o.deleteById(pkval)
        return render_template('ok_dialog.html', msg=f"Location ID {pkval} deleted.")

    # INSERT action (from modal submission)
    if action is not None and action == 'insert':
        d = {}
        d['name'] = request.form.get('name')
        d['latitude'] = request.form.get('latitude')
        d['longitude'] = request.form.get('longitude')
        d['description'] = request.form.get('description')
        d['submitted_by'] = session['user']['user_id']  # Auto-set from session

        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html', msg=f"Location '{o.data[0]['name']}' added successfully!")
        else:
            return render_template('locations/add.html', obj=o)

    # UPDATE action
    if action is not None and action == 'update':
        o.getById(pkval)
        o.data[0]['name'] = request.form.get('name')
        o.data[0]['latitude'] = request.form.get('latitude')
        o.data[0]['longitude'] = request.form.get('longitude')
        o.data[0]['description'] = request.form.get('description')

        if o.verify_update():
            o.update()
            return render_template('ok_dialog.html', msg="Location updated successfully!")
        else:
            return render_template('locations/manage.html', obj=o)

    # ADD new location (pkval = 'new')
    if pkval == 'new':
        o.createBlank()
        return render_template('locations/add.html', obj=o)

    # EDIT specific location (pkval = numeric ID)
    else:
        o.getById(pkval)
        return render_template('locations/manage.html', obj=o)

@app.route('/api/locations',methods=['GET'])
def api_locations():
    """API endpoint to return all locations as JSON for map markers"""
    if checkSession() == False:
        return redirect('/login')

    o = location()
    o.getAll('name')

    # Convert to GeoJSON format for Mapbox
    features = []
    for loc in o.data:
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(loc['longitude']), float(loc['latitude'])]
            },
            'properties': {
                'location_id': loc['location_id'],
                'name': loc['name'],
                'description': loc['description'] if loc['description'] else '',
                'verified': loc['verified'],
                'submitted_by': loc['submitted_by'],
                'submission_timestamp': str(loc['submission_timestamp'])
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return make_response(geojson, 200, {'Content-Type': 'application/json'})

@app.route('/jumppoints/manage',methods=['GET','POST'])
def manage_jumppoint():
    if checkSession() == False:
        return redirect('/login')

    o = jumppoint()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    location_id = request.args.get('location_id')
    user_type = session.get('user', {}).get('user_type', 'guest')

    # Check permissions: only registered, trusted, and admin can modify
    if user_type == 'guest' and action in ['insert', 'update', 'delete']:
        return render_template('ok_dialog.html', msg="Guests cannot modify jump points. Please login or register to contribute.")

    # DELETE action
    if action is not None and action == 'delete':
        o.deleteById(pkval)
        return render_template('ok_dialog.html', msg=f"Jump point ID {pkval} deleted.")

    # INSERT action
    if action is not None and action == 'insert':
        d = {}
        d['location_id'] = request.form.get('location_id')
        d['name'] = request.form.get('name')
        d['height_feet'] = request.form.get('height_feet')
        d['difficulty'] = request.form.get('difficulty')
        d['description'] = request.form.get('description')
        d['dangers'] = request.form.get('dangers')
        d['position_description'] = request.form.get('position_description')
        d['submitted_by'] = session['user']['user_id']

        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html', msg=f"Jump point '{o.data[0]['name']}' added successfully!")
        else:
            return render_template('jumppoints/add.html', obj=o, location_id=d['location_id'])

    # UPDATE action
    if action is not None and action == 'update':
        o.getById(pkval)
        o.data[0]['location_id'] = request.form.get('location_id')
        o.data[0]['name'] = request.form.get('name')
        o.data[0]['height_feet'] = request.form.get('height_feet')
        o.data[0]['difficulty'] = request.form.get('difficulty')
        o.data[0]['description'] = request.form.get('description')
        o.data[0]['dangers'] = request.form.get('dangers')
        o.data[0]['position_description'] = request.form.get('position_description')

        if o.verify_update():
            o.update()
            return render_template('ok_dialog.html', msg="Jump point updated successfully!")
        else:
            return render_template('jumppoints/manage.html', obj=o)

    # ADD new jumppoint (pkval = 'new')
    if pkval == 'new':
        o.createBlank()
        # Pre-fill location_id if provided
        if location_id:
            o.data[0]['location_id'] = location_id
        return render_template('jumppoints/add.html', obj=o, location_id=location_id)

    # EDIT specific jumppoint (pkval = numeric ID)
    elif pkval is not None:
        o.getById(pkval)
        if len(o.data) == 0:
            return render_template('ok_dialog.html', msg=f"Jump point ID {pkval} not found.")
        return render_template('jumppoints/manage.html', obj=o)

    # No pkval provided - redirect to main page
    else:
        return redirect('/main')

@app.route('/api/jumppoints/<int:location_id>',methods=['GET'])
def api_jumppoints(location_id):
    """API endpoint to return all jump points for a specific location"""
    if checkSession() == False:
        return redirect('/login')

    o = jumppoint()
    jumps = o.get_by_location(location_id)

    # Convert to simple JSON array
    jump_list = []
    for jump in jumps:
        jump_data = {
            'jump_id': jump['jump_id'],
            'name': jump['name'],
            'height_feet': jump['height_feet'] if jump['height_feet'] else None,
            'difficulty': jump['difficulty'] if jump['difficulty'] else None,
            'description': jump['description'] if jump['description'] else '',
            'dangers': jump['dangers'] if jump['dangers'] else '',
            'position_description': jump['position_description'] if jump['position_description'] else '',
            'verified': jump['verified'],
            'status': jump['status']
        }
        jump_list.append(jump_data)

    return make_response({'jumps': jump_list}, 200, {'Content-Type': 'application/json'})






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
            # Create guest session instead of failing
            create_guest_session()
            return True
        else:
            session['active'] = time.time()
            return True
    else:
        # No session exists - auto-create guest session
        create_guest_session()
        return True  


if __name__ == '__main__':
   app.run(host='0.0.0.0',debug=True)   