from flask import Flask, render_template ,request,jsonify
import pandas as pd
import numpy as np
import database
from math import sqrt

# fetch booking data
# desk_booking will have columns like this in database
# desk_data = {
#     "desk_id": ["D001", "D002", "D003", "D004", "D005"],
#     "desk_location_x": [2, 5, 8, 3, 7],
#     "desk_location_y": [3, 5, 1, 8, 2],
#     "is_available": [True, False, True, True, True]
# }



#  fetch employees data
# employees data will have columns like this in database
# Simulating Employee Data (employee_id, department_id, desk_id, desk_location_x, desk_location_y)
# employee_data = {
#     "employee_id": ["E001", "E002", "E003", "E004"],
#     "department_id": [1, 1, 2, 1],
#     "desk_id": ["D002", "D003", "D001", "D005"],
#     "desk_location_x": [5, 8, 2, 7],
#     "desk_location_y": [5, 1, 3, 2]
# }


# function to find euclidean distance between two employees desk location
# square root( (x2-x1)**2 - (y2-y1)*2 )


def find_nearest_desk(employees,target_employee,desks):
    # Filter colleagues and available desks
    same_dept = employees[employees['department_id'] == target_employee['department_id']]
    available_desks = desks[desks['is_available']]
    
    nearest_desk = None
    min_distance = float('inf')
    
    for _, desk in available_desks.iterrows():
        total_distance = 0
        for _, colleague in same_dept.iterrows():
            total_distance += np.sqrt(
                (desk['desk_location_x'] - colleague['desk_location_x'])**2 +
                (desk['desk_location_y'] - colleague['desk_location_y'])**2
            )
        if total_distance < min_distance:
            min_distance = total_distance
            nearest_desk = desk
            
    return nearest_desk


def main_allocate_task():
        # parse the request data
    data = request.json
    employee_id = data.get('employee_id')

    # load data
    employees,desks = database.load_data()

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
