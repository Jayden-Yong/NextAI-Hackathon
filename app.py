from flask import Flask, render_template ,request,jsonify, url_for, redirect
from dynamic_desk_allocation import main_allocate_task
import ai_function
import pandas as pd
import database as db
import pymysql
import bcrypt

app = Flask(__name__)

# Page routes
# Route for homepage
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/user')
def user():
    return render_template('landing.html')

# Functional routes
# Login verfication
@app.route('/verify-login', methods=['POST'])
def verify_login():
    email = request.form['email']
    password = request.form['password']
    
    accounts = db.load_accounts()

    # Check if the email exists
    if email in accounts['email'].values:
        stored_pw = accounts.loc[accounts['email'] == email,'password_hash'].values[0]

        # Check if the hashed passwords matches
        if bcrypt.checkpw(password.encode('utf-8'), stored_pw.encode('utf-8')):

            # Check user privilege
            if accounts.loc[accounts['email'] == email, 'access'].values[0] == 0:
                return redirect(url_for('admin'))
            elif accounts.loc[accounts['email'] == email, 'access'].values[0] == 1:
                return redirect(url_for('user'))
            
        else:
            error = "Invalid password"
    else:
        error = "Email not found"
    
    return render_template('login.html', error = error)


@app.route('/allocate-desk', methods=['POST'])
def allocate_desk():
    main_allocate_task()


def recommendation_f2f_work():
    return jsonify(ai_function.recommendation_f2f)

def recommendation_meeting():
    return jsonify(ai_function.recommendation_meeting)


if __name__ == '__main__':
    # Runs the app in debug mode
    app.run(debug=True,port=5000)