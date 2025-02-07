import pandas as pd
import pymysql

# (DICT) MySQL configuration
DB_CONFIG = {
    'host':'localhost',
    'user':'root',
    'password':'fop2024',
    'database':'hybridhub'
}

# Connection establisher
def connect_db():
    connection = pymysql.connect(**DB_CONFIG)
    return connection

# SQL command related methods beyond this point
# load data from mysql into pandas dataframe
def load_data():
    employees = pd.read_sql("SELECT * FROM employees",connect_db)
    desks = pd.read_sql("SELECT * FROM desks",connect_db)
    connect_db.close()
    return employees,desks
