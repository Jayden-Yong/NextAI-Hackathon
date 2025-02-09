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
    con = connect_db()
    employees = pd.read_sql("SELECT * FROM employees",con)
    desks = pd.read_sql("SELECT * FROM desks",con)
    con.close()
    return employees,desks


def load_accounts():
    con = connect_db()
    accounts = pd.read_sql("SELECT * FROM accounts",con)
    con.close()
    return accounts