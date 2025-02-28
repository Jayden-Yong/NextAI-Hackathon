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

# Special function to check for intersections between booking intervals
def intervals_intersect(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)

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
    
    bookmeeting = pd.read_sql('SELECT * FROM bookmeeting',con)
    return employees,desks,booking,department,bookmeeting

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

def load_meeting_bookings(target_start, target_end):
    con = connect_db()
    query = text("""SELECT bookmeeting.meetingID, bookmeeting.employeeID, bookmeeting.startTime, bookmeeting.endTime,
                    bookmeeting.deskID, desk.coordX, desk.coordY 
                    FROM bookmeeting JOIN desk ON desk.deskID = bookmeeting.deskID
                """)
    bookings = pd.read_sql(query, con)

    # Convert target start and end datetime strings to datetime objects for comparison
    target_start = datetime.strptime(target_start, "%Y-%m-%d %H:%M:%S")
    target_end = datetime.strptime(target_end, "%Y-%m-%d %H:%M:%S")

    # Filter bookings that intersect with the target_datetime
    filtered_bookings = bookings[
        bookings.apply(lambda row: intervals_intersect(
            target_start, target_end, 
            row['startTime'], row['endTime']
        ), axis=1)
    ]

    return filtered_bookings

def book_meeting(employeeID,deskID,startTime,endTime):
    engine = connect_db()
    query = text("INSERT INTO bookmeeting (employeeID,deskID,startTime,endTime) VALUES(:id,:deskID,:startTime,:endTime)")
    with engine.begin() as con:
        con.execute(query, {"id": employeeID, "deskID": deskID, "startTime": startTime, "endTime": endTime})
        con.commit()

def get_departments():
    con = connect_db()
    query = "SELECT * FROM department"
    depts = pd.read_sql(query, con).to_dict("records")
    return depts

def get_employeeIDs():
    con = connect_db()
    query = "SELECT employeeID from employee"
    ids = pd.read_sql(query, con).to_json(orient="records")
    return ids

def add_employee(employeeID,name,departmentID):
    engine = connect_db()
    query = text("INSERT INTO employee (employeeID,name,departmentID) VALUES (:id,:name,:deptID)")
    with engine.begin() as con:
        con.execute(query, {"id": employeeID, "name": name, "deptID": departmentID})
        con.commit()

def add_account(hashed_password,employeeID):
    engine = connect_db()
    query = text("INSERT INTO accounts (password_hash,employeeID) VALUES (:pwHashed,:id)")
    with engine.begin() as con:
        con.execute(query, {"pwHashed": hashed_password, "id": employeeID})
        con.commit()

def delete_employee(employeeID):
    engine = connect_db()
    query = text("DELETE FROM employee WHERE employeeID = :employeeID")
    with engine.begin() as con:
        con.execute(query, {"employeeID": employeeID})
        con.commit()

def find_employee(employeeID):
    con = connect_db()
    query = f"SELECT * FROM employee WHERE employeeID = '{employeeID}'"
    employeeData = pd.read_sql(query, con).to_dict('records')
    return employeeData

def find_account(employeeID):
    con = connect_db()
    query = f"SELECT * FROM accounts WHERE employeeID = '{employeeID}'"
    accData = pd.read_sql(query, con).to_dict('records')
    return accData

def update_employee(oldID,employeeID,name,departmentID,prefDays):
    engine = connect_db()
    query = text("UPDATE employee SET employeeID = :employeeID, name = :name, departmentID = :deptID, prefDays = :prefDays WHERE employeeID = :oldID")
    with engine.begin() as con:
        con.execute(query, {"employeeID": employeeID, "name": name, "deptID": departmentID, "prefDays": prefDays, "oldID": oldID})
        con.commit()

def get_departments():
    con = connect_db()
    query = "SELECT * FROM department"
    deptDB = pd.read_sql(query,con).to_dict("records")
    return deptDB

def add_department(deptID,name):
    engine = connect_db()
    query = text("INSERT INTO department (departmentID,departmentName) VALUES (:deptID,:name)")
    with engine.begin() as con:
        con.execute(query, {"deptID": deptID, "name": name})
        con.commit()

def delete_department(deptID):
    engine = connect_db()
    query = text("DELETE FROM department WHERE departmentID = :deptID")
    with engine.begin() as con:
        con.execute(query, {"deptID": deptID})
        con.commit()

def find_department(deptID):
    con = connect_db()
    query = f"SELECT * FROM department WHERE departmentID = '{deptID}'"
    deptData = pd.read_sql(query, con).to_dict('records')
    return deptData

def update_department(oldID,deptID,name):
    engine = connect_db()
    query = text("UPDATE department SET departmentID = :deptID, departmentName = :name WHERE departmentID = :oldID")
    with engine.begin() as con:
        con.execute(query, {"deptID": deptID, "name": name, "oldID": oldID})
        con.commit()

def employer_update_profile(name , email , id , departmentName , old_id):
    engine = connect_db()
    query = text("""
        UPDATE employee e
        JOIN accounts a ON e.employeeID = a.employeeID
        JOIN department d ON e.departmentID = d.departmentID
        SET e.name = :name,
            a.email = :email,
            e.employeeID = :new_id,
            d.departmentName = :departmentName
        WHERE e.employeeID = :old_id;
    """)
    with engine.begin() as con:
        con.execute(query, {
            "name": name,
            "email": email,
            "new_id": id,
            "departmentName": departmentName,
            "old_id": old_id
        })

def employee_update_profile(name , email , id , departmentName , prefDays):
    engine = connect_db()
    query = text("""
        UPDATE employee e
        JOIN accounts a ON e.employeeID = a.employeeID
        JOIN department d ON e.departmentID = d.departmentID
        SET e.name = :name,
            a.email = :email,
            e.prefDays = :prefDays,
            d.departmentName = :departmentName
        WHERE e.employeeID = :id;
    """)
    with engine.begin() as con:
        result = con.execute(query, {
            "name": name,
            "email": email,
            "id": id,
            "departmentName": departmentName,
            "prefDays": prefDays
        })

def bind_google(employeeID,email):
    engine = connect_db()
    query = text("UPDATE accounts SET email = :email WHERE employeeID = :id")
    with engine.begin() as con:
        con.execute(query, {"email": email, "id": employeeID})
        con.commit()

def unbind_google(employeeID):
    engine = connect_db()
    query = text("UPDATE accounts SET email = '' WHERE employeeID = :id")
    with engine.begin() as con:
        con.execute(query, {"id": employeeID})
        con.commit()