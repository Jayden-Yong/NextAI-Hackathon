import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
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

def load_employee_data():
    con = connect_db()
    employee_datas = pd.read_sql("SELECT employee.employeeID,accounts.email,employee.name,employee.prefDays,department.departmentName FROM employee JOIN accounts ON employee.employeeID = accounts.employeeID JOIN department ON employee.departmentID = department.departmentID",con)
    return employee_datas

def load_desks():
    con = connect_db()
    desks = pd.read_sql("SELECT * FROM desk",con)
    return desks

def get_bookingIDs():
    con = connect_db()
    ids = pd.read_sql("SELECT bookingID FROM booking",con).to_json(orient='records')
    return ids

def load_desk_bookings():
    con = connect_db()
    bookings = pd.read_sql("SELECT booking.bookingID,booking.employeeID,booking.deskID,booking.date,desk.coordX,desk.coordY FROM booking JOIN desk ON booking.deskID = desk.deskID",con)
    filter = bookings[bookings['deskID'].str.startswith("D")]
    return filter

def load_active_team(departmentID,date):
    con = connect_db()
    query = "SELECT employee.employeeID,booking.date FROM booking JOIN employee ON employee.employeeID = booking.employeeID WHERE employee.departmentID = %s AND DATE(booking.date) = %s"
    members = pd.read_sql(query, con, params=(departmentID,date))
    active_count = len(members)
    return active_count

def book_desk(employeeID,deskID,datetime):
    engine = connect_db()
    query = text("INSERT INTO booking (employeeID, deskID, date) VALUES (:id,:deskID,:date)")
    with engine.begin() as con:
        con.execute(query, {"id": employeeID, "deskID": deskID, "date": datetime})
        con.commit()

def load_meeting_bookings(target_datetime):
    con = connect_db()
    query = text("""SELECT bookmeeting.meetingID, bookmeeting.employeeID, bookmeeting.startTime, bookmeeting.endTime,
                    bookmeeting.deskID, desk.coordX, desk.coordY 
                    FROM bookmeeting JOIN desk ON desk.deskID = bookmeeting.deskID
                    WHERE :datetime BETWEEN bookmeeting.startTime AND bookmeeting.endTime""")
    bookings = pd.read_sql(query, con, params={"datetime": target_datetime})
    return bookings