import pandas as pd
import pymysql

from config import DB_CONFIG

# Connection establisher
def connect_db():
    connection = pymysql.connect(**DB_CONFIG)
    return connection

# SQL command related methods beyond this point
# load data from mysql into pandas dataframe
def load_data():

    # employees data
    employees = pd.read_sql("SELECT * FROM employees",connect_db)

    # desks details data
    desks = pd.read_sql("SELECT * FROM desks",connect_db)

    # booking details data
    booking = pd.read_sql("SELECT * FROM booking",connect_db)

    # department data for employees
    department = pd.read_sql("SELECT * FROM department",connect_db)
    connect_db.close()
    return employees,desks,booking,department
