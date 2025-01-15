from flask import Flask, render_template ,request,jsonify
from dynamic_desk_allocation import find_nearest_desk
import pandas as pd
import pymysql

app = Flask(__name__)

# MySQL configuration
DB_CONFIG = {
    'host':'',
    'user':'',
    'password':'',
    'database':''
}
# Route for homepage
@app.route('/')
def home():
    return render_template('index.html')



@app.route('/allocate-desk', methods=['POST'])
def allocate_desk():
     
    # parse the request data
    data = request.json
    employee_id = data.get('employee_id')

    # load data
    employees,desks = load_data()

    # find target employee
    target_employee = employees[employees['employee_id']==employee_id]

    if target_employee.empty:
        return jsonify({'error':'Employee not found'}),404
    
    target_employee = target_employee.iloc[0]

    # call the desk allocation function
    assigned_desk = find_nearest_desk(employees,target_employee,desks)

    if assigned_desk is not None:
        return jsonify({"assigned_desk":assigned_desk['desk_id']})
    
    else:
        return jsonify({'error':'no available desks'}),400

if __name__ == '__main__':
    # Runs the app in debug mode
    app.run(debug=True)