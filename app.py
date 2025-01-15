from flask import Flask, render_template ,request,jsonify
from dynamic_desk_allocation import main_allocate_task
import pandas as pd
import pymysql

app = Flask(__name__)


# Route for homepage
@app.route('/')
def home():
    return render_template('index.html')



@app.route('/allocate-desk', methods=['POST'])
def allocate_desk():
    main_allocate_task()


if __name__ == '__main__':
    # Runs the app in debug mode
    app.run(debug=True)