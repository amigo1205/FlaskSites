-- For a pharmacist account.

DROP TABLE IF EXISTS `Coordinator`;
CREATE TABLE `Coordinator` (
  `firstName` varchar(75) NOT NULL DEFAULT '',
  `lastName` varchar(75) NOT NULL DEFAULT '',
  `email` varchar(100) NOT NULL DEFAULT '',
  `organization` varchar(150) DEFAULT '',
  `province` varchar(3) NOT NULL DEFAULT '',
  `city` varchar(50) DEFAULT '',
  `postal` varchar(7) DEFAULT '',
  `address1` varchar(100) DEFAULT '',
  `address2` varchar(100) DEFAULT '',
  `phone` varchar(20) DEFAULT '',
  `fax` varchar(20) DEFAULT '',
  `dateCreated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dateApproved` timestamp NULL DEFAULT NULL,
  `dateUpdated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `emailActivationToken` varchar(40) DEFAULT NULL,
  `emailActivationExpiry` timestamp NULL DEFAULT NULL,
  `resetPasswordToken` varchar(40) DEFAULT NULL,
  `resetPasswordExpiry` timestamp NULL DEFAULT NULL,
  `coordinatorId` int(11) NOT NULL AUTO_INCREMENT,
  `passwordHash` varchar(64) DEFAULT NULL,
  `status` varchar(15) NOT NULL DEFAULT 'NOTACTIVATED',
  `admin` enum('T','F') DEFAULT 'F',
  `receivesEmails` enum('T','F') DEFAULT 'F',
  `includeInProviderList` enum('T','F') DEFAULT 'F',
  `receivesWaiverEmails` enum('T','F') DEFAULT 'F',
  PRIMARY KEY (`coordinatorId`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=171 DEFAULT CHARSET=latin1;

-- For a patient account
DROP TABLE IF EXISTS `Demographic`;
CREATE TABLE `Demographic` (
  `demographicNo` int(11) DEFAULT NULL,
  `hin` varchar(25) NOT NULL DEFAULT '',
  `ver` varchar(10) NOT NULL DEFAULT '',
  `effDate` varchar(10) NOT NULL DEFAULT '',
  `hcType` varchar(3) NOT NULL DEFAULT '',
  `activeCount` int(11) DEFAULT '1',
  `firstName` varchar(30) NOT NULL DEFAULT '',
  `lastName` varchar(30) DEFAULT '',
  `email` varchar(100) NOT NULL DEFAULT '',
  `phone` varchar(20) DEFAULT '',
  `phone2` varchar(20) DEFAULT '',
  `address` varchar(60) NOT NULL DEFAULT '',
  `city` varchar(20) NOT NULL DEFAULT '',
  `province` varchar(3) NOT NULL DEFAULT '',
  `postal` varchar(7) NOT NULL DEFAULT '',
  `dateOfBirth` varchar(2) NOT NULL DEFAULT '',
  `monthOfBirth` varchar(15) NOT NULL DEFAULT '',
  `yearOfBirth` varchar(4) NOT NULL DEFAULT '',
  `sex` enum('M','F') NOT NULL DEFAULT 'M',
  `familyDoctor` varchar(60) NOT NULL DEFAULT '',
  `spokenLanguage` varchar(60) NOT NULL DEFAULT '',
  `officialLanguage` varchar(60) NOT NULL DEFAULT '',
  `patientStatus` varchar(20) NOT NULL DEFAULT '',
  `patientStatusDate` date DEFAULT NULL,
  `notes` varchar(255) NOT NULL DEFAULT '',
  `dateCreated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dateUpdated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`hin`,`ver`),
  UNIQUE KEY `demographic_no` (`demographicNo`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- For a case instance
DROP TABLE IF EXISTS `Appointment`;
CREATE TABLE `Appointment` (
  `caseId` int(11) NOT NULL,
  `coordinatorId` int(11) NOT NULL AUTO_INCREMENT,
  `demographicNo` int(11) NOT NULL,
  `dateCreated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dateUpdated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `notes` varchar(255) NOT NULL DEFAULT '',
  `reason` varchar(80) NOT NULL DEFAULT '',
  `location` varchar(30) NOT NULL DEFAULT '',
  `resources` varchar(255) NOT NULL DEFAULT '',
  `type` varchar(50) NOT NULL DEFAULT '',
  `name` varchar(50) NOT NULL DEFAULT '',
  `appointmentStartDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `appointmentEndDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `waiverPDF` mediumblob,
  PRIMARY KEY (`caseId`),
  KEY `patient_number` (`demographicNo`),
  KEY `fk_Appointment_1` (`coordinatorId`),
  CONSTRAINT `fk_Appointment_1` FOREIGN KEY (`coordinatorId`) REFERENCES `Coordinator` (`coordinatorId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=173 DEFAULT CHARSET=latin1;
