from flask import Flask, render_template ,request,jsonify, url_for, redirect, session, abort, Response, send_file
from datetime import datetime, timedelta
from functools import wraps
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from current_user_details import get_user_details,get_user_data_df
from sqlalchemy import text
import analytics_graphs
import google.auth.transport.requests
import pathlib
import requests
import json
import pandas as pd
import database as db
import bcrypt
import os

from database import connect_db , employer_update_profile , employee_update_profile, current_user_upcoming_data_desk,current_user_upcoming_data_meeting,colleagues_in_office,available_meeting_room
from sqlalchemy import text

# Allow http transport for OAuth during development (will be removed in production)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "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"

# Google login
GOOGLE_CLIENT_ID = "72353004136-v04m6s1m0g4r801sbofl5uqad6734b3e.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

# Google binding
GOOGLE_BIND_CLIENT_ID = "72353004136-d7d0ma8fomh233m84a61fhsc67sl6i4p.apps.googleusercontent.com"
bind_secrets_file = os.path.join(pathlib.Path(__file__).parent, "bind_secret.json")

bind_flow = Flow.from_client_secrets_file(
    client_secrets_file=bind_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/bind_callback"
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
    id = session['data']['employeeID']
    desk = current_user_upcoming_data_desk(id).to_dict(orient='records')
    meeting = current_user_upcoming_data_meeting(id).to_dict(orient='records')
    colleagues = colleagues_in_office(id).to_dict(orient='records')
    available_meeting = available_meeting_room().to_dict(orient='records')

    return render_template('user.html', current_url=request.path , upcoming_desk = desk,upcoming_meeting = meeting ,colleagues = colleagues, available_meeting = available_meeting)

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
    message = request.args.get('message','')
    return render_template('employee_manager.html', employeeDB=employeeDB, current_url=request.path, message=message)

@app.route('/add_employee')
@login_required
def add_employee():
    depts = db.get_departments()
    id_list = db.get_employeeIDs()
    return render_template('add_employee.html',current_url=request.path, depts=depts, id_json=id_list)

@app.route('/delete_employee/<string:employeeID>', methods=["GET","POST"])
@login_required
def delete_employee(employeeID):
    db.delete_employee(employeeID)
    message = f"Employee {employeeID} has been deleted successfully."
    return redirect(url_for('employee_manager', message=message))

@app.route('/edit_employee/<string:employee_id>', methods=["GET","POST"])
@login_required
def edit_employee(employee_id):
    employeeData = db.find_employee(employee_id)
    accData = db.find_account(employee_id)
    access = accData[0]['access']
    depts = db.get_departments()
    id_list = db.get_employeeIDs()
    return render_template('edit_employee.html', current_url=request.path, depts=depts, employeeData=employeeData[0], access=access, id_json=id_list)


@app.route('/add_department')
@login_required
def add_department():
    deptDB = db.get_departments()
    message = request.args.get('message','')
    return render_template('add_department.html', current_url=request.path, deptDB=deptDB, message=message)

@app.route('/delete_department/<string:deptID>', methods=["GET","POST"])
@login_required
def delete_department(deptID):
    db.delete_department(deptID)
    message = f"Department {deptID} has been deleted successfully."
    return redirect(url_for('add_department', message=message))

@app.route('/edit_department/<string:deptID>', methods=["GET","POST"])
@login_required
def edit_department(deptID):
    deptData = db.find_department(deptID)
    deptDB = db.get_departments()
    return render_template('edit_department.html', current_url=request.path, deptDB=deptDB, deptData=deptData[0])


@app.route('/ai_assistant')
def ai_assistant():
    return render_template('ai_assistant.html',current_url=request.path)


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
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

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
            'google': 'true',
            'access': access,
            'email': email,
            'picture': id_info.get("picture"),
            'date': now.strftime("%d %B %Y"),
            'day': now.strftime("%A"),
            'login-time': now.strftime("%H:%M:%S"),
            'data': data
        })
        session["user_details"] = [data]

        return redirect(url_for('admin' if access == 0 else 'user'))
    else:
            error = "This email is not connected with us."
            return render_template('login.html', error = error)

# Google Bind OAuth
@app.route("/google_bind")
def google_bind():
    authorization_url, state = bind_flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/bind_callback")
def bind_callback():
    bind_flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = bind_flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_BIND_CLIENT_ID
    )

    # Bind the Google account with employee ID
    email = id_info.get("email")
    db.bind_google(session['data']['employeeID'],email)

    session.update({
        'google': 'true',
        'email': email,
        'picture': id_info.get("picture")
    })

    return redirect(url_for('employee_setting' if session['access'] == 1 else 'employer_setting'))

# Unbind Google
@app.route('/unbind_google')
@login_required
def unbind_google():
    # Set email to null for the current user in session
    db.unbind_google(session['data']['employeeID'])

    session.pop('picture', None)
    session.update({
        'google': 'false',
        'email': session['data']['employeeID']
    })

    message = "Google account has been removed"

    return redirect(url_for('employee_setting' if session['access'] == 1 else 'employer_setting', message=message))


# Login verfication
@app.route('/verify-login', methods=['POST'])
def verify_login():
    email = request.form['id']
    password = request.form['password']
    
    accounts = db.load_accounts()
    employees = db.load_employees()

    # Check if the email exists
    if email in accounts['email'].values or email in accounts['employeeID'].values:
        stored_pw = accounts.loc[(accounts['email'] == email) | (accounts['employeeID'] == email),'password_hash'].values[0]

        # Check if the hashed passwords matches
        if bcrypt.checkpw(password.encode('utf-8'), stored_pw.encode('utf-8')):

            # Check user privilege
            access = int(accounts.loc[(accounts['email'] == email) | (accounts['employeeID'] == email), 'access'].values[0])
            data = employees.loc[employees['employeeID'] == accounts.loc[(accounts['email'] == email) | (accounts['employeeID'] == email), 'employeeID'].values[0], ['employeeID', 'name', 'prefDays', 'departmentID']].to_dict('records')[0]
            now = datetime.now()
            session.update({
                'google': 'false',
                'access': access,
                'email': email,
                'date': now.strftime("%d %B %Y"),
                'day': now.strftime("%A"),
                'login-time': now.strftime("%H:%M:%S"),
                'data': data
            })
            session["user_details"] = [data]

            return redirect(url_for('admin' if access == 0 else 'user'))
            
        else:
            error = "Invalid password"
    else:
        error = "Email not found"
    
    return render_template('login.html', error = error)


@app.route('/logout')
def logout():
    # Revoke the Google OAuth token
    if 'credentials' in session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        revoke = requests.post('https://oauth2.googleapis.com/revoke',
                               params={'token': credentials.token},
                               headers={'content-type': 'application/x-www-form-urlencoded'})
        if revoke.status_code == 200:
            print("Token revoked successfully.")
        else:
            print("Failed to revoke token.")

    session.clear()
    return redirect(url_for('home'))

# employer settings
@app.route('/employer_setting',methods = ['GET','POST'])
def employer_setting():
    employeesDB = db.load_employee_data()
    current_user = get_user_data_df(get_user_details())
    id = session['data']['employeeID']
    details = employeesDB.loc[employeesDB['employeeID'] == id, ['employeeID','email','name','prefDays','departmentName']].to_dict('records')[0]
    splitted_name = details['name'].split(' ')
    if len(splitted_name)<=1:
        first_name = splitted_name[0]
        last_name = ""
    else:
        first_name = splitted_name[0]
        splitted_name.pop(0)
        last_name = ' '.join(splitted_name)
    
    job = details['departmentName']
    email = details['email']

    message = request.args.get('message','')
    return render_template('employer_setting.html',current_url = request.path ,job = job,email = email,first_name = first_name,last_name = last_name ,id = id, message=message)

@app.route('/update_employer_profile',methods = ['POST'])
def update_employer_profile():
    data = request.get_json()

    name = f"{data.get('first_name')} {data.get('last_name')}"
    email = data.get('email')
    id = data.get('id')
    departmentName = data.get('department_name')

    current_user = get_user_data_df(get_user_details())
    old_id = current_user['employeeID'].iloc[0]

    current_user['employeeID'] = id
    session['data']['name'] = name
    session['user_details'] = [current_user.to_dict(orient="records")[0]]
    session.modified = True
    try:
        employer_update_profile(name=name,email=email,id=id,departmentName=departmentName,old_id = old_id)
        return jsonify({"success": True, "message": "Profile updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# employee settings
@app.route('/employee_setting' ,methods = ['GET','POST'])
def employee_setting():
    employeesDB = db.load_employee_data()
    current_user = get_user_data_df(get_user_details())
    id = current_user['employeeID'].iloc[0]
    details = employeesDB.loc[employeesDB['employeeID'] == id, ['employeeID','email','name','prefDays','departmentName']].to_dict('records')[0]
    splitted_name = details['name'].split(' ')
    if len(splitted_name)<=1:
        first_name = splitted_name[0]
        last_name = ""
    else:
        first_name = splitted_name[0]
        splitted_name.pop(0)
        last_name = ' '.join(splitted_name)
    
    
    job = details['departmentName']
    email = details['email']
    prefDays = details['prefDays']

    message = request.args.get('message','')
    return render_template('employee_setting.html',current_url = request.path ,job = job,email = email,first_name = first_name,last_name = last_name ,id = id,prefDays = prefDays, message=message )

@app.route('/update_employee_profile',methods = ['POST'])
def update_employee_profile():
    data = request.get_json()

    name = f"{data.get('first_name')} {data.get('last_name')}"
    email = data.get('email')
    id = data.get('id')
    departmentName = data.get('department_name')
    prefDays = data.get('prefDays')

    current_user = get_user_data_df(get_user_details())

    current_user['prefDays'] = prefDays
    session['data']['name'] = name
    session['user_details'] = [current_user.to_dict(orient="records")[0]]
    session.modified = True
    try:
        employee_update_profile(name=name ,email=email ,id=id ,departmentName=departmentName ,prefDays = prefDays)
        return jsonify({"success": True, "message": "Profile updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# account password changing route
@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({"success": False, "error": "New password not provided."}), 400

    import re
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', new_password):
        return jsonify({"success": False, "error": "Password is too weak."}), 400

    current = session.get('data')
    current_id = current['employeeID']
    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    engine = connect_db()
    query = text("""
        UPDATE accounts
        SET password_hash = :password
        WHERE employeeID = :id;
    """)
    with engine.begin() as con:
        con.execute(query, {
            "password": hashed_pw,
            "id": current_id
        })

    return jsonify({"success": True, "message": "Password changed successfully!"})


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
    session['total_rooms'] = len(desks_pd[desks_pd['deskID'].str.startswith('M')])

    # Preset target datetime to current date and time
    target_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Sets default booking time length to 1hr
    target_end = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    # Prepare booked data as a json
    meeting_booked = db.load_meeting_bookings(target_start, target_end)
    booked_json = pd.DataFrame(meeting_booked).to_json(orient="records")
    total_booked = len(meeting_booked)
    total_left = session['total_rooms'] - total_booked

    message = request.args.get('message', '')
    return render_template("book_meeting.html", current_url=request.path, desks_json=desks_json, booked_json=booked_json, booked=total_booked, left=total_left, message=message)

@app.route('/update_meeting_bookingData', methods=['POST'])
@login_required
def update_meeting_bookingData():
    # Retrieve updates on new target datetime and duration
    req_datetime = request.json.get('selectedDatetime')
    req_duration = request.json.get('duration')

    # Prepare the data in the required formats
    duration = int(req_duration)
    target_start = datetime.strptime(req_datetime,"%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
    target_end = (datetime.strptime(req_datetime,"%Y-%m-%dT%H:%M") + timedelta(hours=duration)).strftime("%Y-%m-%d %H:%M:%S")

    # Prepare booked data as a json
    meeting_booked = db.load_meeting_bookings(target_start, target_end)
    booked_json = pd.DataFrame(meeting_booked).to_dict(orient="records")
    total_booked = len(meeting_booked)
    total_left = session['total_rooms'] - total_booked

    # Prepare a json as a response
    response_data = {
        'booked': booked_json,
        'total_booked': total_booked,
        'total_left': total_left
    }

    return jsonify(response_data)

@app.route('/meeting_booking_logic', methods=['POST'])
@login_required
def meeting_booking_logic():
    deskID = request.form["meetingID"]
    req_start = request.form["target-start"]
    duration = int(request.form["duration"])

    # Prepare data before inserting into database
    target_start = datetime.strptime(req_start,"%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
    target_end = (datetime.strptime(req_start,"%Y-%m-%dT%H:%M") + timedelta(hours=duration)).strftime("%Y-%m-%d %H:%M:%S")

    # Execute booking query function
    db.book_meeting(session['data']['employeeID'],deskID,target_start,target_end)

    message = f"Your reservation for meeting room {deskID} on {target_start} for {duration} hours has been confirmed."
    return redirect(url_for('book_meeting', message=message))


@app.route('/add_employee_logic', methods=["POST"])
@login_required
def add_employee_logic():
    newID = request.form['id']
    password = request.form['password']
    name = request.form['name']
    deptID = request.form['deptID']

    # Hash the password with bcrypt
    Hpassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Execute queries to add employee to database
    db.add_employee(newID,name,deptID)
    db.add_account(Hpassword,newID)

    message = "New employee has been added successfully."
    return redirect(url_for('employee_manager', message=message))

@app.route('/update_employee_logic', methods=["POST"])
@login_required
def update_employee_logic():
    oldID = request.form['oldID']
    id = request.form['id']
    name = request.form['name']
    deptID = request.form['deptID']
    if 'prefDays' in request.form:
        prefDays = request.form['prefDays']
    else:
        prefDays = None

    db.update_employee(oldID,id,name,deptID,prefDays)

    message = f"Account data for {oldID} was updated."
    return redirect(url_for('employee_manager', message=message))


@app.route('/add_department_logic', methods=["POST"])
@login_required
def add_department_logic():
    deptID = request.form['id']
    name = request.form['name']

    db.add_department(deptID,name)

    message = f"Department {deptID} was created successfully."
    return redirect(url_for('add_department', message=message))

@app.route('/update_department_logic', methods=["POST"])
@login_required
def update_department_logic():
    oldID = request.form['oldID']
    id = request.form['id']
    name = request.form['name']

    db.update_department(oldID,id,name)

    message = f"Department data for {oldID} was updated."
    return redirect(url_for('add_department', message=message))


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

# route for employer analytics page
@app.route('/desk_utilization_graph')
def desk_utilization_graph():
    try:
        img0 = analytics_graphs.daily_desk_utilization()
        return Response(img0, mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')
    

@app.route('/department_booking_distribution_graph')
def department_booking_distribution_graph():
    try: 
        img1 = analytics_graphs.department_booking_distribution()
        return Response(img1, mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')

@app.route('/employees_attendance_trend_graph')
def employees_attendance_trend_graph():
    try:
        img2 = analytics_graphs.employees_attendance_trend()
        return Response(img2 ,mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')


@app.route('/desk_availability_status_graph')
def desk_availability_status_graph():
    try:
        img3 = analytics_graphs.desk_availability_status()
        return Response(img3,mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')

@app.route('/preferred_days_by_employees_graph')
def preferred_days_by_employees_graph():
    try:
        img4 = analytics_graphs.preferred_days_by_employees()
        return Response(img4,mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')

@app.route('/weekly_peak_office_usage_graph')
def weekly_peak_office_usage_graph():
    try:
        img5 = analytics_graphs.weekly_peak_office_usage()
        return Response(img5,mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')

# route for employee analytics graph
@app.route('/personal_desk_booking_history_graph')
def personal_desk_booking_history_graph():
    try:
        user_details = get_user_details()
        img0 = analytics_graphs.personal_desk_booking_history(user_details)
        return Response(img0,mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')

@app.route('/preferred_desk_usage_frequency_graph')
def preferred_desk_usage_frequency_graph():
    try:
        user_details = get_user_details()
        img1 = analytics_graphs.preferred_desk_usage_frequency(user_details)
        return Response(img1,mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')

@app.route('/average_monthly_attendance_graph')
def average_monthly_attendance_graph():
    try:
        user_details = get_user_details()
        img2 = analytics_graphs.average_monthly_attendance(user_details)
        return Response(img2,mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')

@app.route('/comparison_of_booking_patterns_with_peers_graph')
def comparison_of_booking_patterns_with_peers_graph():
    try:
        user_details = get_user_details()
        img3 = analytics_graphs.comparison_of_booking_patterns_with_peers(user_details)
        return Response(img3,mimetype='image/png')
    except:
        return send_file('static/images/not-enough-data.png',mimetype='image/png')


if __name__ == '__main__':
    # Runs the app in debug mode
    app.run(debug=True,port=5000)
