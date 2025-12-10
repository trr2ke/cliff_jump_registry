"""
Cliff Jump Registry - Main Application
========================================

A Flask-based web application for managing a community-driven cliff jumping location registry.

Features:
- Location and jump point management with interactive map (Mapbox)
- User authentication with role-based permissions (guest, registered, admin)
- Jump log diary for tracking personal jumps
- Reviews and ratings system for locations
- Real-time safety condition reporting
- Community flagging system for content moderation

Author: Theodore Reed
License: MIT
"""

from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, make_response, jsonify
from flask_session import Session
from datetime import timedelta
from user import user
from location import location
from jumppoint import jumppoint
from jumplog import jumplog
from review import review
from safetyreport import safetyreport
from flag import flag
import time
import yaml
from pathlib import Path

# Initialize Flask application with custom static URL path
app = Flask(__name__, static_url_path='')

# Flask session configuration
app.config['SECRET_KEY'] = 'sdfvbgfdjeR5y5r'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in filesystem (flask_session directory)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)  # Sessions expire after 5 hours of inactivity

# Initialize Flask-Session extension
sess = Session()
sess.init_app(app)

def create_guest_session():
    """
    Create a guest session with default guest user credentials.

    This allows unauthenticated users to browse the site with limited permissions.
    Guest users can view locations and data but cannot create or modify content.
    """
    session['user'] = {
        'user_id': 0,
        'username': 'Guest',
        'email': 'guest@example.com',
        'user_type': 'guest'
    }
    session['active'] = time.time()  # Track last activity time for session timeout

@app.route('/')
def home():
    """
    Home route - Entry point for the application.

    Automatically creates a guest session if user is not logged in,
    then redirects to the main dashboard.
    """
    if 'user' not in session or session.get('user') is None:
        create_guest_session()
    return redirect('/main')

@app.context_processor
def inject_user():
    """
    Context processor to make current user data available in all templates.

    Returns:
        dict: Dictionary with 'me' key containing current user session data
    """
    return dict(me=session.get('user'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login authentication.

    GET: Display login form
    POST: Process login credentials and create authenticated session

    Returns:
        On successful login: Redirect to main dashboard
        On failed login: Login page with error message
    """
    un = request.form.get('name')  # Username or email
    pw = request.form.get('password')

    if un is not None and pw is not None:
        u = user()
        # Attempt login with username/email and password
        if u.tryLogin(un, pw):
            session['user'] = u.data[0]  # Store user data in session
            session['active'] = time.time()  # Track session activity
            return redirect('main')
        else:
            return render_template('login.html', title='Login', msg='Incorrect username or password.')

    # Display login form for GET requests
    m = 'Welcome back'
    return render_template('login.html', title='Login', msg=m)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Handle user logout.

    Clears the current user session and redirects to home,
    which will automatically create a new guest session.
    """
    if session.get('user') is not None:
        del session['user']
        del session['active']
    # Redirect to home, which will auto-login as guest
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle new user registration.

    GET: Display registration form
    POST: Process registration data and create new user account

    Returns:
        On successful registration: Login page with success message
        On validation errors: Registration form with error messages
    """
    o = user()
    action = request.args.get('action')

    if action is not None and action == 'insert':
        # Collect registration form data
        d = {}
        d['username'] = request.form.get('username')
        d['email'] = request.form.get('email')
        d['user_type'] = 'registered'  # New users default to 'registered' role
        d['password'] = request.form.get('password')
        d['password2'] = request.form.get('password2')
        o.set(d)

        # Validate and insert new user
        if o.verify_new():
            o.insert()
            return render_template('login.html', title='Login', msg='Registration successful! Please log in.')
        else:
            return render_template('register.html', obj=o)
    else:
        # Display blank registration form
        o.createBlank()
        return render_template('register.html', obj=o)

@app.route('/users/manage', methods=['GET', 'POST'])
def manage_user():
    """
    Admin-only route for managing users (CRUD operations).

    Supports:
    - LIST: Display all users (no pkval)
    - CREATE: Add new user (pkval='new', action='insert')
    - READ: View single user (pkval=ID)
    - UPDATE: Edit user (pkval=ID, action='update')
    - DELETE: Remove user (pkval=ID, action='delete')

    Args (query params):
        action: CRUD operation ('insert', 'update', 'delete')
        pkval: Primary key value or 'new' for create
    """
    o = user()
    action = request.args.get('action')
    pkval = request.args.get('pkval')

    # DELETE operation
    if action is not None and action == 'delete':
        o.deleteById(pkval)
        return render_template('ok_dialog.html', msg=f"Record ID {pkval} Deleted.")

    # INSERT operation - Create new user
    if action is not None and action == 'insert':
        d = {}
        d['username'] = request.form.get('username')
        d['email'] = request.form.get('email')
        d['user_type'] = request.form.get('user_type')
        d['password'] = request.form.get('password')
        d['password2'] = request.form.get('password2')
        o.set(d)

        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html', msg=f"User {o.data[0][o.pk]} added.")
        else:
            return render_template('users/add.html', obj=o)

    # UPDATE operation - Edit existing user
    if action is not None and action == 'update':
        o.getById(pkval)
        o.data[0]['username'] = request.form.get('username')
        o.data[0]['email'] = request.form.get('email')
        o.data[0]['user_type'] = request.form.get('user_type')
        o.data[0]['password'] = request.form.get('password')
        o.data[0]['password2'] = request.form.get('password2')

        if o.verify_update():
            o.update()
            return render_template('ok_dialog.html', msg="User updated. ")
        else:
            return render_template('users/manage.html', obj=o)

    # LIST operation - Display all users
    if pkval is None:
        o.getAll()
        return render_template('users/list.html', obj=o)

    # CREATE operation - Show form for new user
    if pkval == 'new':
        o.createBlank()
        return render_template('users/add.html', obj=o)

    # READ operation - Display single user for editing
    else:
        o.getById(pkval)
        return render_template('users/manage.html', obj=o)

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

    # Check permissions for add/edit/delete: only registered and admin
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

    # Get safety report info for each location
    from safetyreport import safetyreport
    sr = safetyreport()

    # Convert to GeoJSON format for Mapbox
    features = []
    for loc in o.data:
        # Get latest safety report for this location
        latest_reports = sr.get_latest_by_location(loc['location_id'])
        has_safety_report = len(latest_reports) > 0
        is_unsafe = has_safety_report and latest_reports[0]['is_safe'] == 0

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
                'submitted_by': loc['submitted_by'] if 'submitted_by' in loc else None,
                'has_safety_report': has_safety_report,
                'is_unsafe': is_unsafe
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

    # Check permissions: only registered and admin can modify
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
        # Convert empty strings to None for integer fields
        d['height_feet'] = request.form.get('height_feet') if request.form.get('height_feet') else None
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
        # Convert empty strings to None for integer fields
        o.data[0]['height_feet'] = request.form.get('height_feet') if request.form.get('height_feet') else None
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
            'position_description': jump['position_description'] if jump['position_description'] else ''
        }
        jump_list.append(jump_data)

    return make_response({'jumps': jump_list}, 200, {'Content-Type': 'application/json'})

@app.route('/jumplogs/manage',methods=['GET','POST'])
def manage_jumplog():
    """Manage personal jump logs (diary)"""
    if checkSession() == False:
        return redirect('/login')

    o = jumplog()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    user_type = session.get('user', {}).get('user_type', 'guest')
    user_id = session.get('user', {}).get('user_id')

    # Guests cannot create jump logs
    if user_type == 'guest' and action in ['insert', 'update', 'delete']:
        return render_template('ok_dialog.html', msg="Guests cannot create jump logs. Please login or register.")

    # DELETE action - users can only delete their own logs
    if action is not None and action == 'delete':
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            o.deleteById(pkval)
            return render_template('ok_dialog.html', msg=f"Jump log deleted.")
        else:
            return render_template('ok_dialog.html', msg="You can only delete your own jump logs.")

    # INSERT action
    if action is not None and action == 'insert':
        d = {}
        d['user_id'] = user_id  # Auto-set from session
        d['location_id'] = request.form.get('location_id')
        d['jump_date'] = request.form.get('jump_date')
        # Convert empty strings to None for integer fields
        d['height_jumped'] = request.form.get('height_jumped') if request.form.get('height_jumped') else None
        d['notes'] = request.form.get('notes')
        d['photo_url'] = request.form.get('photo_url')
        d['is_private'] = 1 if request.form.get('is_private') == 'on' else 0

        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html', msg=f"Jump log added successfully!")
        else:
            return render_template('jumplogs/add.html', obj=o)

    # UPDATE action - users can only update their own logs
    if action is not None and action == 'update':
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            o.data[0]['location_id'] = request.form.get('location_id')
            o.data[0]['jump_date'] = request.form.get('jump_date')
            # Convert empty strings to None for integer fields
            o.data[0]['height_jumped'] = request.form.get('height_jumped') if request.form.get('height_jumped') else None
            o.data[0]['notes'] = request.form.get('notes')
            o.data[0]['photo_url'] = request.form.get('photo_url')
            o.data[0]['is_private'] = 1 if request.form.get('is_private') == 'on' else 0

            if o.verify_update():
                o.update()
                return render_template('ok_dialog.html', msg="Jump log updated successfully!")
            else:
                return render_template('jumplogs/manage.html', obj=o)
        else:
            return render_template('ok_dialog.html', msg="You can only edit your own jump logs.")

    # LIST - show user's own jump logs
    if pkval is None:
        o.get_by_user(user_id)
        return render_template('jumplogs/list.html', obj=o)

    # ADD new log
    if pkval == 'new':
        o.createBlank()
        return render_template('jumplogs/add.html', obj=o)

    # EDIT specific log
    else:
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            return render_template('jumplogs/manage.html', obj=o)
        else:
            return render_template('ok_dialog.html', msg="You can only view your own jump logs.")

@app.route('/reviews/manage',methods=['GET','POST'])
def manage_review():
    """Manage location reviews and ratings"""
    if checkSession() == False:
        return redirect('/login')

    o = review()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    location_id = request.args.get('location_id')
    user_type = session.get('user', {}).get('user_type', 'guest')
    user_id = session.get('user', {}).get('user_id')

    # Guests cannot create reviews
    if user_type == 'guest' and action in ['insert', 'update', 'delete']:
        return render_template('ok_dialog.html', msg="Guests cannot create reviews. Please login or register.")

    # DELETE action - users can only delete their own reviews
    if action is not None and action == 'delete':
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            o.deleteById(pkval)
            return render_template('ok_dialog.html', msg=f"Review deleted.")
        else:
            return render_template('ok_dialog.html', msg="You can only delete your own reviews.")

    # INSERT action
    if action is not None and action == 'insert':
        d = {}
        d['user_id'] = user_id  # Auto-set from session
        d['location_id'] = request.form.get('location_id')
        d['rating'] = request.form.get('rating')
        d['safety_rating'] = request.form.get('safety_rating')
        d['access_rating'] = request.form.get('access_rating')
        d['review_text'] = request.form.get('review_text')
        d['visit_date'] = request.form.get('visit_date')

        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html', msg=f"Review added successfully!")
        else:
            return render_template('reviews/add.html', obj=o, location_id=d.get('location_id'))

    # UPDATE action - users can only update their own reviews
    if action is not None and action == 'update':
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            o.data[0]['rating'] = request.form.get('rating')
            o.data[0]['safety_rating'] = request.form.get('safety_rating')
            o.data[0]['access_rating'] = request.form.get('access_rating')
            o.data[0]['review_text'] = request.form.get('review_text')
            o.data[0]['visit_date'] = request.form.get('visit_date')

            if o.verify_update():
                o.update()
                return render_template('ok_dialog.html', msg="Review updated successfully!")
            else:
                return render_template('reviews/manage.html', obj=o)
        else:
            return render_template('ok_dialog.html', msg="You can only edit your own reviews.")

    # ADD new review (check this FIRST before list views)
    if pkval == 'new':
        o.createBlank()
        return render_template('reviews/add.html', obj=o, location_id=location_id)

    # LIST reviews by location
    if location_id is not None:
        o.get_by_location(location_id)
        return render_template('reviews/list.html', obj=o, location_id=location_id)

    # LIST - show user's own reviews
    if pkval is None:
        o.get_by_user(user_id)
        return render_template('reviews/list.html', obj=o)

    # EDIT specific review
    else:
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            return render_template('reviews/manage.html', obj=o)
        else:
            return render_template('ok_dialog.html', msg="You can only view your own reviews.")

@app.route('/api/reviews/<int:location_id>',methods=['GET'])
def api_reviews(location_id):
    """API endpoint to get reviews for a location"""
    if checkSession() == False:
        return redirect('/login')

    o = review()
    o.get_by_location(location_id)

    # Get average ratings
    averages = o.get_location_average_ratings(location_id)

    return make_response({
        'reviews': o.data,
        'averages': averages
    }, 200, {'Content-Type': 'application/json'})

@app.route('/safetyreports/manage',methods=['GET','POST'])
def manage_safetyreport():
    """Manage safety condition reports"""
    if checkSession() == False:
        return redirect('/login')

    o = safetyreport()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    location_id = request.args.get('location_id')
    user_type = session.get('user', {}).get('user_type', 'guest')
    user_id = session.get('user', {}).get('user_id')

    # Guests cannot create safety reports
    if user_type == 'guest' and action in ['insert', 'update', 'delete']:
        return render_template('ok_dialog.html', msg="Guests cannot create safety reports. Please login or register.")

    # DELETE action - users can only delete their own reports (or admin can delete)
    if action is not None and action == 'delete':
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            o.deleteById(pkval)
            return render_template('ok_dialog.html', msg=f"Safety report deleted.")
        else:
            return render_template('ok_dialog.html', msg="You can only delete your own safety reports.")

    # INSERT action
    if action is not None and action == 'insert':
        d = {}
        d['user_id'] = user_id  # Auto-set from session
        d['location_id'] = request.form.get('location_id')
        d['report_date'] = request.form.get('report_date')
        # Convert empty strings to None for integer fields
        d['water_depth'] = request.form.get('water_depth') if request.form.get('water_depth') else None
        d['water_temp'] = request.form.get('water_temp') if request.form.get('water_temp') else None
        d['conditions'] = request.form.get('conditions')
        d['hazards'] = request.form.get('hazards')
        d['is_safe'] = 1 if request.form.get('is_safe') == '1' else 0
        d['photo_url'] = request.form.get('photo_url')

        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html', msg=f"Safety report added successfully!")
        else:
            return render_template('safetyreports/add.html', obj=o, location_id=d.get('location_id'))

    # UPDATE action
    if action is not None and action == 'update':
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            o.data[0]['location_id'] = request.form.get('location_id')
            o.data[0]['report_date'] = request.form.get('report_date')
            # Convert empty strings to None for integer fields
            o.data[0]['water_depth'] = request.form.get('water_depth') if request.form.get('water_depth') else None
            o.data[0]['water_temp'] = request.form.get('water_temp') if request.form.get('water_temp') else None
            o.data[0]['conditions'] = request.form.get('conditions')
            o.data[0]['hazards'] = request.form.get('hazards')
            o.data[0]['is_safe'] = 1 if request.form.get('is_safe') == '1' else 0
            o.data[0]['photo_url'] = request.form.get('photo_url')

            if o.verify_update():
                o.update()
                return render_template('ok_dialog.html', msg="Safety report updated successfully!")
            else:
                return render_template('safetyreports/manage.html', obj=o)
        else:
            return render_template('ok_dialog.html', msg="You can only edit your own safety reports.")

    # ADD new report (check this FIRST before list views)
    if pkval == 'new':
        o.createBlank()
        return render_template('safetyreports/add.html', obj=o, location_id=location_id)

    # LIST reports by location
    if location_id is not None:
        o.get_by_location(location_id, 20)
        return render_template('safetyreports/list.html', obj=o, location_id=location_id)

    # LIST - show recent unsafe reports
    if pkval is None:
        o.get_recent_unsafe_reports(30)
        return render_template('safetyreports/list.html', obj=o)

    # EDIT specific report
    else:
        o.getById(pkval)
        if len(o.data) > 0 and (o.data[0]['user_id'] == user_id or user_type == 'admin'):
            return render_template('safetyreports/manage.html', obj=o)
        else:
            return render_template('ok_dialog.html', msg="You can only view your own safety reports.")

@app.route('/api/safetyreports/<int:location_id>',methods=['GET'])
def api_safetyreports(location_id):
    """API endpoint to get safety reports for a location"""
    if checkSession() == False:
        return redirect('/login')

    o = safetyreport()
    reports = o.get_by_location(location_id, 5)

    return make_response({
        'reports': reports
    }, 200, {'Content-Type': 'application/json'})

@app.route('/admin/analytics')
def admin_analytics():
    """Admin analytics dashboard with platform statistics"""
    user_type = session.get('user', {}).get('user_type')
    if user_type != 'admin':
        return render_template('ok_dialog.html', msg="Access denied. Admin user required.")

    from user import user
    from location import location
    from jumppoint import jumppoint
    from jumplog import jumplog
    from review import review
    from safetyreport import safetyreport

    # Initialize objects to access database
    u_obj = user()
    l_obj = location()
    jp_obj = jumppoint()
    jl_obj = jumplog()
    r_obj = review()
    sr_obj = safetyreport()

    analytics = {}

    # User statistics
    u_obj.cur.execute(f"SELECT user_type, COUNT(*) as count FROM Users GROUP BY user_type")
    analytics['users_by_type'] = {row['user_type']: row['count'] for row in u_obj.cur}

    u_obj.cur.execute(f"SELECT COUNT(*) as total FROM Users")
    analytics['total_users'] = u_obj.cur.fetchone()['total']

    # Content statistics
    l_obj.cur.execute(f"SELECT COUNT(*) as total FROM Locations")
    analytics['total_locations'] = l_obj.cur.fetchone()['total']

    l_obj.cur.execute(f"SELECT COUNT(*) as total FROM Locations WHERE flag_count > 0")
    analytics['flagged_locations'] = l_obj.cur.fetchone()['total']

    # Total unresolved flags across all content
    f_obj = flag()
    f_obj.cur.execute(f"SELECT COUNT(*) as total FROM Flags WHERE is_resolved = 0")
    analytics['unresolved_flags'] = f_obj.cur.fetchone()['total']

    jp_obj.cur.execute(f"SELECT COUNT(*) as total FROM JumpPoints")
    analytics['total_jumppoints'] = jp_obj.cur.fetchone()['total']

    r_obj.cur.execute(f"SELECT COUNT(*) as total FROM Reviews")
    analytics['total_reviews'] = r_obj.cur.fetchone()['total']

    jl_obj.cur.execute(f"SELECT COUNT(*) as total FROM JumpLogs")
    analytics['total_jumplogs'] = jl_obj.cur.fetchone()['total']

    sr_obj.cur.execute(f"SELECT COUNT(*) as total FROM SafetyReports")
    analytics['total_safetyreports'] = sr_obj.cur.fetchone()['total']

    sr_obj.cur.execute(f"SELECT COUNT(*) as total FROM SafetyReports WHERE is_safe=0")
    analytics['unsafe_reports'] = sr_obj.cur.fetchone()['total']

    # Most reviewed locations
    r_obj.cur.execute(f"""
        SELECT l.name, l.location_id, COUNT(*) as review_count, AVG(r.rating) as avg_rating
        FROM Reviews r
        JOIN Locations l ON r.location_id = l.location_id
        GROUP BY l.location_id
        ORDER BY review_count DESC
        LIMIT 5
    """)
    analytics['most_reviewed'] = [dict(row) for row in r_obj.cur]

    # Most active users (by contributions)
    u_obj.cur.execute(f"""
        SELECT u.username, u.user_id, u.user_type,
        (SELECT COUNT(*) FROM Reviews WHERE user_id = u.user_id) +
        (SELECT COUNT(*) FROM JumpLogs WHERE user_id = u.user_id) +
        (SELECT COUNT(*) FROM SafetyReports WHERE user_id = u.user_id) +
        (SELECT COUNT(*) FROM Locations WHERE submitted_by = u.user_id) as total_contributions
        FROM Users u
        WHERE u.user_type != 'guest'
        ORDER BY total_contributions DESC
        LIMIT 10
    """)
    analytics['top_contributors'] = [dict(row) for row in u_obj.cur]

    # Recent activity (last 10 reviews)
    r_obj.cur.execute(f"""
        SELECT r.*, l.name as location_name, u.username
        FROM Reviews r
        JOIN Locations l ON r.location_id = l.location_id
        JOIN Users u ON r.user_id = u.user_id
        ORDER BY r.created_date DESC
        LIMIT 10
    """)
    analytics['recent_reviews'] = [dict(row) for row in r_obj.cur]

    # Recent safety reports
    sr_obj.cur.execute(f"""
        SELECT sr.*, l.name as location_name, u.username
        FROM SafetyReports sr
        JOIN Locations l ON sr.location_id = l.location_id
        JOIN Users u ON sr.user_id = u.user_id
        ORDER BY sr.report_timestamp DESC
        LIMIT 10
    """)
    analytics['recent_safetyreports'] = [dict(row) for row in sr_obj.cur]

    # Flagged content for admin review (most flagged items)
    l_obj.cur.execute(f"""
        SELECT l.location_id, l.name, l.flag_count,
               COUNT(f.flag_id) as active_flags,
               GROUP_CONCAT(DISTINCT u.username SEPARATOR ', ') as flagged_by_users
        FROM Locations l
        LEFT JOIN Flags f ON f.flaggable_type = 'location' AND f.flaggable_id = l.location_id AND f.is_resolved = 0
        LEFT JOIN Users u ON f.user_id = u.user_id
        WHERE l.flag_count > 0
        GROUP BY l.location_id, l.name, l.flag_count
        ORDER BY l.flag_count DESC
        LIMIT 10
    """)
    analytics['flagged_locations_detail'] = [dict(row) for row in l_obj.cur]

    return render_template('admin/analytics.html', analytics=analytics)


# ============================================================================
# FLAG ROUTES - Community content moderation
# ============================================================================

@app.route('/flags/add', methods=['GET', 'POST'])
def add_flag():
    """
    Submit a flag for content (location, jumppoint, review, or safety report).

    GET: Display flag submission form
    POST: Process flag submission

    Query params:
        type: Content type ('location', 'jumppoint', 'review', 'safetyreport')
        id: Content ID
    """
    if checkSession() == False:
        return redirect('/login')

    # Only registered and admin users can flag content
    if session['user']['user_type'] == 'guest':
        return render_template('ok_dialog.html', msg='You must be logged in to flag content.')

    if request.method == 'POST':
        # Process flag submission - get values from form data
        flaggable_type = request.form.get('flaggable_type')
        flaggable_id = request.form.get('flaggable_id')

        f = flag()
        d = {
            'flaggable_type': flaggable_type,
            'flaggable_id': flaggable_id,
            'user_id': session['user']['user_id'],
            'flag_reason': request.form.get('flag_reason'),
            'flag_category': request.form.get('flag_category')
        }
        f.set(d)

        if f.verify_new():
            f.insert()

            # Update flag_count for the content
            if flaggable_type == 'location':
                loc = location()
                loc.cur.execute("UPDATE Locations SET flag_count = flag_count + 1 WHERE location_id = %s", [flaggable_id])
                loc.conn.commit()
            elif flaggable_type == 'jumppoint':
                jp = jumppoint()
                jp.cur.execute("UPDATE JumpPoints SET flag_count = flag_count + 1 WHERE jump_id = %s", [flaggable_id])
                jp.conn.commit()

            return render_template('ok_dialog.html', msg='Thank you! Your flag has been submitted and will be reviewed by an administrator.', continue_url='/main')
        else:
            return render_template('flags/add.html', obj=f, flaggable_type=flaggable_type, flaggable_id=flaggable_id, categories=f.categories)

    # Display flag form (GET request) - get values from URL query parameters
    flaggable_type = request.args.get('flaggable_type')
    flaggable_id = request.args.get('flaggable_id')

    f = flag()
    f.createBlank()
    f.data[0]['flaggable_type'] = flaggable_type
    f.data[0]['flaggable_id'] = flaggable_id

    # Get content name for display
    content_name = ''
    if flaggable_type == 'location':
        loc = location()
        loc.getById(flaggable_id)
        if len(loc.data) > 0:
            content_name = loc.data[0]['name']
    elif flaggable_type == 'jumppoint':
        jp = jumppoint()
        jp.getById(flaggable_id)
        if len(jp.data) > 0:
            content_name = jp.data[0]['name']

    return render_template('flags/add.html', obj=f, flaggable_type=flaggable_type, flaggable_id=flaggable_id, content_name=content_name, categories=f.categories)


@app.route('/flags/view')
def view_flags():
    """
    View all flags for a specific piece of content.

    Query params:
        type: Content type
        id: Content ID
    """
    if checkSession() == False:
        return redirect('/login')

    flaggable_type = request.args.get('flaggable_type')
    flaggable_id = request.args.get('flaggable_id')

    f = flag()
    # Admins can see resolved flags, others only see active flags
    include_resolved = (session['user']['user_type'] == 'admin')
    flags = f.get_by_content(flaggable_type, flaggable_id, include_resolved)

    return render_template('flags/list.html', obj=f, flags=flags, flaggable_type=flaggable_type, flaggable_id=flaggable_id)


@app.route('/admin/flags')
def admin_flags():
    """
    Admin interface for reviewing all unresolved flags.

    Displays all flagged content organized by type and flag count.
    """
    if checkSession() == False:
        return redirect('/login')

    # Only admins can access this page
    if session['user']['user_type'] != 'admin':
        return render_template('ok_dialog.html', msg='Access denied. Admin privileges required.')

    f = flag()
    flags = f.get_unresolved_flags(limit=100)

    return render_template('admin/flags.html', obj=f, flags=flags)


@app.route('/flags/resolve', methods=['POST'])
def resolve_flag():
    """
    Admin route to resolve a flag.

    POST params:
        flag_id: ID of flag to resolve
        resolution_notes: Admin notes about the resolution
        action: 'resolve_only' or 'resolve_and_delete'
    """
    if checkSession() == False:
        return redirect('/login')

    # Only admins can resolve flags
    if session['user']['user_type'] != 'admin':
        return render_template('ok_dialog.html', msg='Access denied. Admin privileges required.')

    flag_id = request.form.get('flag_id')
    resolution_notes = request.form.get('resolution_notes', '')
    delete_content = request.form.get('delete_content') == '1'

    f = flag()
    f.getById(flag_id)

    if len(f.data) == 0:
        return jsonify({'status': 'error', 'message': 'Flag not found.'})

    flaggable_type = f.data[0]['flaggable_type']
    flaggable_id = f.data[0]['flaggable_id']

    # Resolve the flag
    if f.resolve_flag(flag_id, session['user']['user_id'], resolution_notes):
        # Decrement flag_count for the content
        if flaggable_type == 'location':
            loc = location()
            loc.cur.execute("UPDATE Locations SET flag_count = GREATEST(flag_count - 1, 0) WHERE location_id = %s", [flaggable_id])
            loc.conn.commit()
        elif flaggable_type == 'jumppoint':
            jp = jumppoint()
            jp.cur.execute("UPDATE JumpPoints SET flag_count = GREATEST(flag_count - 1, 0) WHERE jump_id = %s", [flaggable_id])
            jp.conn.commit()

        # If admin chose to delete the content as well
        if delete_content:
            if flaggable_type == 'location':
                loc = location()
                loc.deleteById(flaggable_id)
            elif flaggable_type == 'jumppoint':
                jp = jumppoint()
                jp.deleteById(flaggable_id)

            return jsonify({'status': 'success', 'message': 'Flag resolved and content deleted.'})

        return jsonify({'status': 'success', 'message': 'Flag resolved successfully.'})
    else:
        return jsonify({'status': 'error', 'message': f'Error resolving flag: {", ".join(f.errors)}'})


@app.route('/session', methods=['GET', 'POST'])
def session_test():
    """Development/debugging route to display current session data."""
    return f"{session}"

@app.route('/main')
def main():
    """
    Main dashboard route displaying the interactive map of cliff jump locations.

    Loads Mapbox API token from config and renders the main page with map interface.
    """
    if checkSession() == False:
        return redirect('/login')

    # Load Mapbox token from configuration file
    config = yaml.safe_load(Path('config.yml').read_text())
    mapbox_token = config['mapbox']['token']
    return render_template('main.html', title='Main menu', mapbox_token=mapbox_token)

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files (CSS, JS, images) from the static directory."""
    return send_from_directory('static', path)

def checkSession():
    """
    Validate user session and handle session timeout.

    Checks if the user has an active session and if it has timed out (500 seconds of inactivity).
    If session is expired or doesn't exist, automatically creates a guest session.

    Returns:
        bool: Always returns True (maintains guest session as fallback)
    """
    if 'active' in session.keys():
        timeSinceAct = time.time() - session['active']

        # Check if session has timed out (500 seconds = ~8.3 minutes)
        if timeSinceAct > 500:
            session['msg'] = 'Your session has timed out.'
            create_guest_session()  # Convert to guest session
            return True
        else:
            session['active'] = time.time()  # Update last activity timestamp
            return True
    else:
        # No session exists - auto-create guest session
        create_guest_session()
        return True  


if __name__ == '__main__':
    # Run Flask development server on all network interfaces
    app.run(host='0.0.0.0', debug=True)   