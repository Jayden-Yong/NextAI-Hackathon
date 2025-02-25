
# database description training prompt for vanna
ddl = """CREATE DATABASE IF NOT EXISTS `hybridhub` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `hybridhub`;

-- Table structure for table `department`
DROP TABLE IF EXISTS `department`;
CREATE TABLE `department` (
  `departmentID` VARCHAR(3) NOT NULL,
  `departmentName` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`departmentID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for table `employee`
DROP TABLE IF EXISTS `employee`;
CREATE TABLE `employee` (
  `employeeID` VARCHAR(6) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `prefDays` VARCHAR(5) DEFAULT NULL,
  `departmentID` VARCHAR(3) NOT NULL,
  PRIMARY KEY (`employeeID`),
  UNIQUE KEY `employeeID_UNIQUE` (`employeeID`),
  KEY `departmentID_idx` (`departmentID`),
  CONSTRAINT `departmentID` FOREIGN KEY (`departmentID`) REFERENCES `department` (`departmentID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for table `desk`
DROP TABLE IF EXISTS `desk`;
CREATE TABLE `desk` (
  `deskID` VARCHAR(6) NOT NULL,
  `coordX` DOUBLE NOT NULL,
  `coordY` DOUBLE NOT NULL,
  PRIMARY KEY (`deskID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for table `accounts`
DROP TABLE IF EXISTS `accounts`;
CREATE TABLE `accounts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `employeeID` VARCHAR(6) NOT NULL,
  `access` INT NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `employeeID_UNIQUE` (`employeeID`),
  CONSTRAINT `employeeID_foreign` FOREIGN KEY (`employeeID`) REFERENCES `employee` (`employeeID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for table `booking`
DROP TABLE IF EXISTS `booking`;
CREATE TABLE `booking` (
  `bookingID` INT NOT NULL AUTO_INCREMENT,
  `employeeID` VARCHAR(6) NOT NULL,
  `deskID` VARCHAR(6) NOT NULL,
  `date` DATE NOT NULL,
  PRIMARY KEY (`bookingID`),
  KEY `employeeID_idx` (`employeeID`),
  KEY `deskID_idx` (`deskID`),
  CONSTRAINT `deskID` FOREIGN KEY (`deskID`) REFERENCES `desk` (`deskID`) ON UPDATE CASCADE,
  CONSTRAINT `employeeID` FOREIGN KEY (`employeeID`) REFERENCES `employee` (`employeeID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"""


# documentation description training prompt for vanna 
documentation = """The 'hybridhub' database is designed to manage office space bookings efficiently. It comprises five primary tables: department, employee, desk, accounts, and booking. Below is a concise overview of each table, its columns, and the relationships between them:

1. department

Purpose: Stores information about the various departments within the organization.
Columns:
departmentID (VARCHAR(3)): Unique identifier for each department.
departmentName (VARCHAR(45)): Name of the department.
Constraints:
PRIMARY KEY on departmentID.
2. employee

Purpose: Contains details about employees.
Columns:
employeeID (VARCHAR(6)): Unique identifier for each employee.
name (VARCHAR(45)): Employee's name.
prefDays (VARCHAR(5)): Preferred working days of the employee.
departmentID (VARCHAR(3)): Identifier linking the employee to a department.
Constraints:
PRIMARY KEY on employeeID.
UNIQUE KEY on employeeID.
FOREIGN KEY (departmentID) references department (departmentID) with ON UPDATE CASCADE.
3. desk

Purpose: Represents the desks available for booking.
Columns:
deskID (VARCHAR(6)): Unique identifier for each desk.
coordX (DOUBLE): X-coordinate of the desk's location.
coordY (DOUBLE): Y-coordinate of the desk's location.
Constraints:
PRIMARY KEY on deskID.
4. accounts

Purpose: Manages user accounts for system access.
Columns:
id (INT): Auto-incremented unique identifier for each account.
email (VARCHAR(255)): User's email address.
password_hash (VARCHAR(255)): Hashed password for authentication.
employeeID (VARCHAR(6)): Identifier linking the account to an employee.
access (INT): Access level of the user, defaulting to '1'.
Constraints:
PRIMARY KEY on id.
UNIQUE KEY on email.
UNIQUE KEY on employeeID.
FOREIGN KEY (employeeID) references employee (employeeID) with ON DELETE CASCADE and ON UPDATE CASCADE.
5. booking

Purpose: Records desk bookings made by employees.
Columns:
bookingID (INT): Auto-incremented unique identifier for each booking.
employeeID (VARCHAR(6)): Identifier of the employee making the booking.
deskID (VARCHAR(6)): Identifier of the desk being booked.
date (DATE): Date of the booking.
Constraints:
PRIMARY KEY on bookingID.
FOREIGN KEY (employeeID) references employee (employeeID) with ON UPDATE CASCADE.
FOREIGN KEY (deskID) references desk (deskID) with ON UPDATE CASCADE.
Relationships:

The employee table is linked to the department table via the departmentID foreign key, establishing which department an employee belongs to.
The accounts table is connected to the employee table through the employeeID foreign key, associating user accounts with their respective employees.
The booking table links to both the employee and desk tables via employeeID and deskID foreign keys, respectively, indicating which employee has booked which desk on a given date.
This structured documentation provides a clear overview of the hybridhub database schema, detailing each table's purpose, columns, constraints, and the relationships between tables."""