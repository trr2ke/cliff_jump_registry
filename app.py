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

Author: Theodore Russell
License: MIT
"""

from flask import Flask
from flask import render_template
from flask import request,session, redirect, url_for, send_from_directory,make_response
from flask_session import Session
from datetime import timedelta
from user import user
from location import location
from jumppoint import jumppoint
from jumplog import jumplog
from review import review
from safetyreport import safetyreport
import time
import yaml
from pathlib import Path

# Initialize Flask application
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
            session['user'] = u.data[0]
            session['active'] = time.time()
            return redirect('main')
        else:
            return render_template('login.html', title='Login', msg='Incorrect username or password.')
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

@app.route('/locations/flag',methods=['POST'])
def flag_location():
    """Flag a location for admin review"""
    if checkSession() == False:
        return redirect('/login')

    user_type = session.get('user', {}).get('user_type', 'guest')
    user_id = session.get('user', {}).get('user_id')

    if user_type == 'guest':
        return render_template('ok_dialog.html', msg="Please login to flag content.")

    location_id = request.form.get('location_id')
    flag_reason = request.form.get('flag_reason', 'No reason provided')

    o = location()
    o.getById(location_id)
    if len(o.data) > 0:
        o.data[0]['is_flagged'] = 1
        o.data[0]['flag_reason'] = flag_reason
        o.data[0]['flagged_by'] = user_id
        o.data[0]['flagged_date'] = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        o.update()
        return render_template('ok_dialog.html', msg="Location flagged for admin review. Thank you for helping keep our community safe!")
    else:
        return render_template('ok_dialog.html', msg="Location not found.")

@app.route('/locations/unflag',methods=['POST'])
def unflag_location():
    """Unflag a location (admin only)"""
    if checkSession() == False:
        return redirect('/login')

    user_type = session.get('user', {}).get('user_type')
    if user_type != 'admin':
        return render_template('ok_dialog.html', msg="Only admins can unflag content.")

    location_id = request.form.get('location_id')

    o = location()
    o.getById(location_id)
    if len(o.data) > 0:
        o.data[0]['is_flagged'] = 0
        o.data[0]['flag_reason'] = None
        o.data[0]['flagged_by'] = None
        o.data[0]['flagged_date'] = None
        o.update()
        return render_template('ok_dialog.html', msg="Location unflagged successfully.")
    else:
        return render_template('ok_dialog.html', msg="Location not found.")

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

    l_obj.cur.execute(f"SELECT COUNT(*) as total FROM Locations WHERE is_flagged=1")
    analytics['flagged_locations'] = l_obj.cur.fetchone()['total']

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

    # Flagged locations for admin review
    l_obj.cur.execute(f"""
        SELECT l.*, u.username as flagged_by_username
        FROM Locations l
        LEFT JOIN Users u ON l.flagged_by = u.user_id
        WHERE l.is_flagged = 1
        ORDER BY l.flagged_date DESC
        LIMIT 10
    """)
    analytics['flagged_locations_detail'] = [dict(row) for row in l_obj.cur]

    return render_template('admin/analytics.html', analytics=analytics)


@app.route('/session',methods = ['GET','POST'])
def session_test():
    return f"{session}"
@app.route('/main')
def main():
    if checkSession() == False:
        return redirect('/login')
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