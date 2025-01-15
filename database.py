import pandas as pd
import pymysql

# load data from mysql into pandas dataframe
def load_data():
    connection = pymysql.connect(**DB_CONFIG)
    employees = pd.read_sql("SELECT * FROM employees",connection)
    desks = pd.read_sql("SELECT * FROM desks",connection)
    connection.close()
    return employees,desks
