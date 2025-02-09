from flask import Flask, render_template ,request,jsonify, url_for
from dynamic_desk_allocation import main_allocate_task
import ai_function
import pandas as pd
import pymysql

app = Flask(__name__)


# Route for homepage
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/verify-login', methods=['POST'])
def verify_login():
    username = request.form['userID']
    password = request.form['password']

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