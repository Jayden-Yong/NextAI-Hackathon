import pandas as pd
import pymysql
from sqlalchemy import create_engine
from config import DB_CONFIG

# host user password database 
password = DB_CONFIG.get("password")
database = DB_CONFIG.get("database")
# Connection establisher
def connect_db():
    url = f"mysql+pymysql://root:{password}@localhost:3306/{database}"
    connection = create_engine(url)
    return connection

# SQL command related methods beyond this point
# load data from mysql into pandas dataframe
def load_allData():
    con = connect_db()
    # employees data
    employees = pd.read_sql("SELECT * FROM employee",con)

    # desks details data
    desks = pd.read_sql("SELECT * FROM desk",con)

    # booking details data
    booking = pd.read_sql("SELECT * FROM booking",con)

    # department data for employees
    department = pd.read_sql("SELECT * FROM department",con)
    
    return employees,desks,booking,department

def load_employees():
    con = connect_db()
    employees = pd.read_sql("SELECT * FROM employee",con)
    return employees

def load_accounts():
    con = connect_db()
    accounts = pd.read_sql("SELECT * FROM accounts",con)
    return accounts