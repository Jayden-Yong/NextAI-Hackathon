from flask import Flask, render_template ,request,jsonify, url_for, redirect, session, abort, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from dynamic_desk_allocation import main_allocate_task
from current_user_details import user_data
import google.auth.transport.requests
import pathlib
import requests
import ai_function
import pandas as pd
import database as db
import bcrypt
import os

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

# Page routes
# Route for homepage
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/admin')
def admin():
    if 'email' in session:
        data = session.get('data')
        return render_template('admin.html', data=data)
    else:
        return redirect(url_for('home'))

@app.route('/user')
def user():
    if 'email' in session:
        data = session.get('data')
        return render_template('user.html', data=data)
    else:
        return redirect(url_for('home'))


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
        if accounts.loc[accounts['email'] == email, 'access'].values[0] == 0:
            data = employees.loc[employees['employeeID'] == accounts.loc[accounts['email'] == email, 'employeeID'].values[0], ['employeeID', 'name', 'prefDays', 'departmentID']].to_dict('records')[0]
            session['email'] = email
            session['picture'] = id_info.get("picture")
            session['data'] = data
            return redirect(url_for('admin'))
        elif accounts.loc[accounts['email'] == email, 'access'].values[0] == 1:
            data = employees.loc[employees['employeeID'] == accounts.loc[accounts['email'] == email, 'employeeID'].values[0], ['employeeID', 'name', 'prefDays', 'departmentID']].to_dict('records')[0]
            session['email'] = email
            session['picture'] = id_info.get("picture")
            session['data'] = data
            return redirect(url_for('user'))
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
            if accounts.loc[accounts['email'] == email, 'access'].values[0] == 0:
                data = employees.loc[employees['employeeID'] == accounts.loc[accounts['email'] == email, 'employeeID'].values[0], ['employeeID', 'name', 'prefDays', 'departmentID']].to_dict('records')[0]
                session['email'] = email
                session['data'] = data
                return redirect(url_for('admin'))
            elif accounts.loc[accounts['email'] == email, 'access'].values[0] == 1:
                data = employees.loc[employees['employeeID'] == accounts.loc[accounts['email'] == email, 'employeeID'].values[0], ['employeeID', 'name', 'prefDays', 'departmentID']].to_dict('records')[0]
                session['email'] = email
                session['data'] = data
                return redirect(url_for('user'))
            
        else:
            error = "Invalid password"
    else:
        error = "Email not found"
    
    return render_template('login.html', error = error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/allocate-desk', methods=['POST'])
def allocate_desk():
    main_allocate_task()

@app.route('/recommendation-f2f-work',methods=['POST'])
def recommendation_f2f_work():
    return (ai_function.recommendation_f2f)

@app.route('/recommendation-meeting',methods=['POST'])
def recommendation_meeting():
    return (ai_function.recommendation_meeting)


if __name__ == '__main__':
    # Runs the app in debug mode
    app.run(debug=True,port=5000)