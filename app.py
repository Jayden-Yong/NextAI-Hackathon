from flask import Flask, render_template ,request,jsonify, url_for, redirect, session
from dynamic_desk_allocation import main_allocate_task
from current_user_details import user_data
import ai_function
import pandas as pd
import database as db
import pymysql
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Page routes
# Route for homepage
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/admin')
def admin():
    if 'email' in session:
        data = session.get('data')
        return render_template('admin.html')
    else:
        return redirect(url_for('home'))

@app.route('/user')
def user():
    if 'email' in session:
        data = session.get('data')
        return render_template('user.html')
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('data', None)
    return redirect(url_for('home'))

# Functional routes
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