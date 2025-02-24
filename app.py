from flask import Flask, render_template ,request,jsonify, url_for, redirect, session, abort
from datetime import datetime
from functools import wraps
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from dynamic_desk_allocation import main_allocate_task
import google.auth.transport.requests
import pathlib
import requests
import json
import ai_function
import pandas as pd
import database as db
import bcrypt
import os

from database import connect_db
from sqlalchemy import text

# Allow http transport for OAuth during development (will be removed in production)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "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"

GOOGLE_CLIENT_ID = "72353004136-v04m6s1m0g4r801sbofl5uqad6734b3e.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

# Decorator for page protection (@login_required)
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'email' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Page routes
# Route for homepage
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', current_url=request.path)

@app.route('/user')
@login_required
def user():
    return render_template('user.html', current_url=request.path)

@app.route('/desk_manager')
@login_required
def desk_manager():
    desks = db.load_desks().to_dict('records')
    desk_count = sum(1 for desk in desks if desk['deskID'].startswith('D'))
    meeting_count = sum(1 for meeting in desks if meeting['deskID'].startswith('M'))
    desks_json = pd.DataFrame(desks).to_json(orient='records')  
    return render_template('customize_desk.html', desks_json=desks_json, meetings=meeting_count, desks=desk_count, current_url=request.path)

@app.route('/employee_manager')
@login_required
def employee_manager():
    employeeDB = db.load_employee_data().to_dict('records')
    return render_template('employee_manager.html', employeeDB=employeeDB, current_url=request.path)

@app.route('/edit_employee/<string:employee_id>')
@login_required
def edit_employee(employee_id):
    employeesDB = db.load_employee_data()
    details = employeesDB.loc[employeesDB['employeeID'] == employee_id, ['employeeID','email','name','prefDays','departmentName']].to_dict('records')[0]
    return render_template('edit_employee.html', details=details)


# Functional routes

# Google OAuth
@app.route("/google_login")
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    email = id_info.get("email")
    accounts = db.load_accounts()
    employees = db.load_employees()

    # Check if the email exists
    if email in accounts['email'].values:
        # Check user privilege
        access = int(accounts.loc[accounts['email'] == email, 'access'].values[0])
        data = employees.loc[employees['employeeID'] == accounts.loc[accounts['email'] == email, 'employeeID'].values[0], ['employeeID', 'name', 'prefDays', 'departmentID']].to_dict('records')[0]
        now = datetime.now()
        session.update({
            'access': access,
            'email': email,
            'picture': id_info.get("picture"),
            'date': now.strftime("%d %B %Y"),
            'day': now.strftime("%A"),
            'login-time': now.strftime("%H:%M:%S"),
            'data': data
        })

        return redirect(url_for('admin' if access == 0 else 'user'))
    else:
            error = "Email not found"
            return render_template('login.html', error = error)


# Login verfication
@app.route('/verify-login', methods=['POST'])
def verify_login():
    email = request.form['email']
    password = request.form['password']
    
    accounts = db.load_accounts()
    employees = db.load_employees()

    # Check if the email exists
    if email in accounts['email'].values:
        stored_pw = accounts.loc[accounts['email'] == email,'password_hash'].values[0]

        # Check if the hashed passwords matches
        if bcrypt.checkpw(password.encode('utf-8'), stored_pw.encode('utf-8')):

            # Check user privilege
            access = int(accounts.loc[accounts['email'] == email, 'access'].values[0])
            data = employees.loc[employees['employeeID'] == accounts.loc[accounts['email'] == email, 'employeeID'].values[0], ['employeeID', 'name', 'prefDays', 'departmentID']].to_dict('records')[0]
            now = datetime.now()
            session.update({
                'access': access,
                'email': email,
                'date': now.strftime("%d %B %Y"),
                'day': now.strftime("%A"),
                'login-time': now.strftime("%H:%M:%S"),
                'data': data
            })

            return redirect(url_for('admin' if access == 0 else 'user'))
            
        else:
            error = "Invalid password"
    else:
        error = "Email not found"
    
    return render_template('login.html', error = error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/book_desk')
@login_required
def book_desk():
    # Preset target date to current date
    target_date = pd.Timestamp(session['date'])
    
    # Preapre desks json for layout rendering
    desks = db.load_desks().to_dict('records')
    desks_json = pd.DataFrame(desks).to_json(orient='records')

    # Retrieve booked desks
    desk_bookings = db.load_desk_bookings()
    desk_bookings['date'] = pd.to_datetime(desk_bookings['date'], format="%d %B %Y")
    booked = desk_bookings[desk_bookings['date'] == target_date].to_dict('records')
    booked_json = pd.DataFrame(booked).to_json(orient='records')
    total = len(booked)

    # Find active team members
    active = db.load_active_team(session['data']['departmentID'],target_date)

    # Creates a dictionary with booking data and save it to a session variable
    bookingData = {
        'target_date'    : target_date,
        'desks_json'     : desks_json,
        'booked_json'    : booked_json,
        'active'         : total,
        'active_members' : active
    }
    session['bookingData'] = bookingData

    message = request.args.get('message', '')
    return render_template('book_desk.html', current_url=request.path, message=message)

@app.route('/update_bookingData', methods=["POST"])
@login_required
def update_bookingData():
    # Retrieve target date and prepare it for comparison
    req_date = request.json.get('selectedDate')
    target_date = pd.Timestamp(req_date).date()

    # Update booked_json and other infos in bookingData session var
    desk_bookings = db.load_desk_bookings()
    desk_bookings['date'] = pd.to_datetime(desk_bookings['date']).dt.date
    booked = desk_bookings[desk_bookings['date'] == target_date].to_dict('records')
    booked_json = pd.DataFrame(booked).to_json(orient='records')
    total = len(booked)

    session['bookingData']['booked_json'] = booked_json
    session['bookingData']['active'] = total
    session['bookingData']['active_members'] = db.load_active_team(session['data']['departmentID'],req_date)

    # Parse booked_json back to a Python object
    booked_data = json.loads(booked_json)

    response_data = {
        'booked': booked_data,
        'active': session['bookingData']['active'],
        'active_members': session['bookingData']['active_members']
    }

    return jsonify(response_data)


@app.route('/booking_logic', methods=["POST"])
@login_required
def booking_logic():
    deskID = request.form['deskID']
    date_string = request.form['target-date']

    # Parse and format the date string
    date_object = datetime.strptime(date_string, "%Y-%m-%d")
    formatted_date = date_object.strftime("%d %B %Y")

    db.book_desk(session['data']['employeeID'],deskID,date_string)
    message = f"Your reservation for desk {deskID} on {formatted_date} has been confirmed."
    return redirect(url_for('book_desk', message=message))


@app.route('/book_meeting')
@login_required
def book_meeting():
    # Preapre desks json for layout rendering
    desks_pd = db.load_desks()
    desks = desks_pd.to_dict('records')
    desks_json = pd.DataFrame(desks).to_json(orient='records')

    # Count the amount of meeting rooms
    meetings = desks_pd[desks_pd['deskID'].str.startswith('M')]

    # Preset target datetime to current date and time
    target_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Prepare booked data as a json
    meeting_booked = db.load_meeting_bookings(target_datetime)
    booked_json = pd.DataFrame(meeting_booked).to_json(orient="records")
    total_booked = len(meeting_booked)
    total_left = len(meetings) - total_booked


    return render_template("book_meeting.html", current_url=request.path, desks_json=desks_json, booked_json=booked_json, booked=total_booked, left=total_left)


@app.route('/allocate-desk', methods=['POST'])
def allocate_desk():
    main_allocate_task()

@app.route('/save_layout', methods=['POST'])
@login_required
def save_layout():
    # Get JSON data from the request
    layout_data = request.get_json()
    
    # Check if the JSON data is provided
    if layout_data is None:
        return jsonify({'error': 'No data provided'}), 400

    engine = connect_db()
    # Use a transactional context manager
    with engine.begin() as conn:
        # Delete all existing records in the desk table
        delete_query = text("DELETE FROM desk")
        conn.execute(delete_query)

        # Insert new records from layout data if provided
        if layout_data:
            for item in layout_data:
                item_id = item.get('id')
                coordX = item.get('coordX')
                coordY = item.get('coordY')

                # Check to make sure it is desk or meeting
                if item_id.startswith('D') or item_id.startswith('M'):
                    desk_id = item_id
                    query = text("""
                        INSERT INTO desk (deskID, coordX, coordY) 
                        VALUES (:id, :x, :y)
                    """)
                    conn.execute(query, {"id": desk_id, "x": coordX, "y": coordY})

    return jsonify({'message': 'Layout saved successfully!'}), 200

@app.route('/recommendation-f2f-work',methods=['POST'])
def recommendation_f2f_work():
    return (ai_function.recommendation_f2f)

@app.route('/recommendation-meeting',methods=['POST'])
def recommendation_meeting():
    return (ai_function.recommendation_meeting)


if __name__ == '__main__':
    # Runs the app in debug mode
    app.run(debug=True,port=5000)