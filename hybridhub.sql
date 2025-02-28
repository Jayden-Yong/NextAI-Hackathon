CREATE DATABASE IF NOT EXISTS `hybridhub` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */;
USE `hybridhub`;

-- Table structure for `accounts`
DROP TABLE IF EXISTS `accounts`;
CREATE TABLE `accounts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) DEFAULT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `employeeID` VARCHAR(6) NOT NULL,
  `access` INT NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `employeeID_UNIQUE` (`employeeID`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  CONSTRAINT `employeeID-foreign` FOREIGN KEY (`employeeID`) REFERENCES `employee` (`employeeID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `booking`
DROP TABLE IF EXISTS `booking`;
CREATE TABLE `booking` (
  `bookingID` INT NOT NULL AUTO_INCREMENT,
  `employeeID` VARCHAR(6) DEFAULT NULL,
  `deskID` VARCHAR(6) DEFAULT NULL,
  `date` DATE NOT NULL,
  PRIMARY KEY (`bookingID`),
  KEY `employeeID_idx` (`employeeID`),
  KEY `deskID_idx` (`deskID`),
  CONSTRAINT `deskID` FOREIGN KEY (`deskID`) REFERENCES `desk` (`deskID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `employeeID` FOREIGN KEY (`employeeID`) REFERENCES `employee` (`employeeID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `bookmeeting`
DROP TABLE IF EXISTS `bookmeeting`;
CREATE TABLE `bookmeeting` (
  `meetingID` INT NOT NULL AUTO_INCREMENT,
  `employeeID` VARCHAR(6) DEFAULT NULL,
  `deskID` VARCHAR(6) DEFAULT NULL,
  `startTime` DATETIME NOT NULL,
  `endTime` DATETIME NOT NULL,
  PRIMARY KEY (`meetingID`),
  KEY `deskID_idx` (`deskID`),
  KEY `employeeID_idx` (`employeeID`),
  CONSTRAINT `meetingDeskID` FOREIGN KEY (`deskID`) REFERENCES `desk` (`deskID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `meetingEmployeeID` FOREIGN KEY (`employeeID`) REFERENCES `employee` (`employeeID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `department`
DROP TABLE IF EXISTS `department`;
CREATE TABLE `department` (
  `departmentID` VARCHAR(3) NOT NULL,
  `departmentName` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`departmentID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `desk`
DROP TABLE IF EXISTS `desk`;
CREATE TABLE `desk` (
  `deskID` VARCHAR(6) NOT NULL,
  `coordX` DOUBLE NOT NULL,
  `coordY` DOUBLE NOT NULL,
  PRIMARY KEY (`deskID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `employee`
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
