getCoordinator = \
'''
select 
firstName                                                 ,
lastName                                                  ,
email                                                      ,
organization                                               ,
province                                                   ,
city                                                       ,
postal                                                ,
address1                                                   ,
address2                                                   ,
phone                                                      ,
fax                                                        ,
DATE_FORMAT(dateCreated,  '%%Y-%%m-%%dT%%TZ') as dateCreated ,
DATE_FORMAT(dateApproved, '%%Y-%%m-%%dT%%TZ') as dateApproved,
DATE_FORMAT(dateUpdated, '%%Y-%%m-%%dT%%TZ') as dateUpdated  ,
emailActivationToken                                     ,
emailActivationExpiry                                    ,
resetPasswordToken                                       ,
resetPasswordExpiry                                      ,
coordinatorId                                                ,
passwordHash                                              ,
status                                                    ,
admin
from Coordinator
where
email = %s
'''


getCoordinators = \
'''
select
firstName,
lastName,
email,
organization,
province,
city,
postal,
address1,
address2,
phone,
fax,
coordinatorId,
status,
admin,
receiveErrorEmails,
includeInProviderList,
receivesWaiverEmails,
receiveAppointmentText,
cellPhone,
receiveErrorText

from Coordinator
order by organization, email
'''

getCoordinatorById = \
'''
select
firstName                                                 ,
lastName                                                  ,
email                                                      ,
organization                                               ,
province                                                   ,
city                                                       ,
postal                                                ,
address1                                                   ,
address2                                                   ,
phone                                                      ,
fax                                                        ,
DATE_FORMAT(dateCreated,  '%%Y-%%m-%%dT%%TZ') as dateCreated ,
DATE_FORMAT(dateApproved, '%%Y-%%m-%%dT%%TZ') as dateApproved,
DATE_FORMAT(dateUpdated, '%%Y-%%m-%%dT%%TZ') as dateUpdated  ,
emailActivationToken                                     ,
emailActivationExpiry                                    ,
resetPasswordToken                                       ,
resetPasswordExpiry                                      ,
coordinatorId                                                ,
passwordHash                                              ,
status                                                    ,
admin
from Coordinator
where
coordinatorId = %s
'''

getUnauthorizedCoordinators = \
'''
select
firstName                                                 ,
lastName                                                  ,
email                                                      ,
organization                                               ,
city                                                       ,
phone                                                      ,
DATE_FORMAT(dateCreated,  '%Y-%m-%dT%T ') as dateCreated ,
coordinatorId                                                ,
status
from Coordinator
where
status = 'UNAUTHORIZED'
order by lastName, firstName, email
'''

setAuthorizedCoordinator = \
'''
update
Coordinator
set
status = 'ACTIVE'
where
coordinatorId = %s
'''



getActivationDetails = \
'''
select
firstName                     ,
lastName                     ,
email                    ,
emailActivationToken   ,
emailActivationExpiry  ,
coordinatorId              ,
status                     ,
organization               ,
city                       ,
phone
from Coordinator
where
coordinatorId = %s
'''

createCoordinatorRecord = \
'''
insert into Coordinator
(
  firstName,
  lastName,
  email,
  organization,
  province,
  city,
  postal,
  address1,
  address2,
  phone,
  fax,
  emailActivationToken   ,
  emailActivationExpiry
  )
  values ( %s, %s, %s, %s, %s, %s, %s, %s, %s , %s ,%s ,%s ,
         DATE_ADD(NOW(), INTERVAL 1 DAY )
         )
'''

updateCoordinator = \
'''
update Coordinator
set
    firstName = %s ,
    lastName = %s ,
    email = %s,
    organization = %s ,
    province = %s ,
    city = %s ,
    postal = %s ,
    address1 = %s ,
    address2 = %s ,
    phone = %s ,
    fax = %s ,
    status = %s ,
    includeInProviderList = %s ,
    receivesWaiverEmails = %s ,
    receiveAppointmentText = %s ,
    cellPhone = %s,
    receiveErrorText = %s,
    receiveErrorEmails = %s,
    admin = %s
    where
    coordinatorId = %s
'''

updateCoordinatorEmailActivation = \
'''
update Coordinator
set
  emailActivationToken  = %s ,
  emailActivationExpiry = DATE_ADD(NOW(), INTERVAL 1 DAY )
  where
  email = %s
'''



setCoordinatorPassword = \
'''
update Coordinator
set passwordHash = %s , status = 'UNAUTHORIZED' ,
emailActivationToken = Null , emailActivationExpiry = Null
where coordinatorId = %s
'''

resetCoordinatorPassword = \
'''
update Coordinator
set passwordHash = %s ,
emailActivationToken = Null , emailActivationExpiry = Null
where coordinatorId = %s
'''

deleteCoordinator = 'delete from Coordinator where coordinatorId=%s'

updateDemographic = \
'''
update Demographic
set
demographicNo = %s
where
hin = %s AND
ver = %s
'''


updateDemographicRecord = \
'''
update Demographic
set
    effDate = %s,
    hcType = %s,
    firstName = %s,
    lastName = %s,
    officialLanguage = %s,
    sex = %s,
    email = %s,
    phone = %s,
    phone2 = %s,
    address = %s,
    city = %s,
    province = %s,
    postal = %s,
    dateOfBirth = %s,
    monthOfBirth = %s,
    yearOfBirth = %s,
    notes = %s,
    spokenLanguage = %s
where
hin = %s AND
ver = %s
'''

insertDemographicRecord = \
'''
insert into Demographic
(
    hin ,
    ver,
    effDate ,
    province ,
    firstName ,
    lastName ,
    officialLanguage ,
    sex ,
    email ,
    phone ,
    phone2 ,
    address ,
    city ,
    hcType ,
    postal,
    dateOfBirth ,
    monthOfBirth ,
    yearOfBirth ,
    notes,
    demographicNo,
    spokenLanguage
)
values
(
    %s ,%s ,%s ,%s ,%s ,
    %s ,%s ,%s ,%s ,%s ,
    %s ,%s ,%s ,%s ,%s ,
    %s ,%s ,%s ,%s ,%s, %s
)
'''


getAppointmentRequestToken = \
'''
select appointmentRequest
from AppointmentRequestToken
where appointmentRequest = %s
'''

setAppointmentRequestToken = \
'''
insert into AppointmentRequestToken
(
appointmentRequest )
VALUES
(
%s )
'''


clearAppointmentRequestToken = \
'''
delete from AppointmentRequestToken
where appointmentRequest = %s
'''

getDemographicInfo = \
'''
select
hin               ,
ver                    ,
DATE_FORMAT(effDate, '%%Y-%%m-%%d') as effDate,
hcType                ,
firstName             ,
lastName              ,
officialLanguage      ,
sex                 ,
email                  ,
phone                  ,
phone2                 ,
address                ,
city                   ,
province               ,
postal            ,
dateOfBirth          ,
monthOfBirth         ,
yearOfBirth          ,
DATE_FORMAT(dateCreated, '%%Y-%%m-%%dT%%TZ') as dateCreated,
notes,
spokenLanguage,
demographicNo
from Demographic
where hin = %s and ver = %s
'''

getAdvertisingCoordinators = \
'''
SELECT
`organization`, `firstName`, `lastName`, `address1`, `address2`, `city`, `province`, `postal`,
`email`, `phone`, `fax`
FROM
`Coordinator`
WHERE
`includeInProviderList` = 'T' AND `status` = 'ACTIVE';
'''


insertAppointmentInfo = \
'''
insert into `Appointment`
(
  caseId,
  coordinatorId,
  demographicNo,
  appointmentStartDate,
  reason,
  notes,
  name,
  waiverPDF,
  appointmentEndDate
)
values
(
  %s, %s, %s, %s, %s, %s, %s, %s, %s
)
'''

getCurrentAppointments = \
'''
SELECT
`Appointment`.`caseId`,
DATE_FORMAT(appointmentStartDate,  '%%Y-%%m-%%d %%T') as appointmentStartDate ,
`Appointment`.`caseId`, `Appointment`.`dateUpdated`, `Appointment`.`notes`, `Appointment`.`reason`,
`Coordinator`.`organization`, `Coordinator`.`address1` as `coordinatorAddr`, `Coordinator`.`city` as `coordinatorCity`,
`Coordinator`.`phone` as `coordinatorPhone`, `Coordinator`.`email` as `coordinatorEmail`, `Coordinator`.`firstName`,
`Coordinator`.`lastName` ,
`Appointment`.`status`,
DATE_FORMAT(appointmentEndDate,  '%%Y-%%m-%%d %%T') as appointmentEndDate ,
TIMESTAMPDIFF( MINUTE, appointmentStartDate , appointmentEndDate ) as appointmentDuration
FROM
`Coordinator` INNER JOIN `Appointment` ON `Coordinator`.`coordinatorId` = `Appointment`.`coordinatorId`
WHERE
`Appointment`.`demographicNo` = %s AND
`Appointment`.`appointmentStartDate` >= CURDATE()
ORDER BY `Appointment`.`appointmentStartDate` ASC;
'''

getPastAppointments = \
'''
SELECT
`Appointment`.`caseId`,
DATE_FORMAT(appointmentStartDate,  '%%Y-%%m-%%d %%T') as appointmentStartDate ,
`Appointment`.`caseId`, `Appointment`.`dateUpdated`, `Appointment`.`notes`, `Appointment`.`reason`,
`Coordinator`.`organization`, `Coordinator`.`address1` as `coordinatorAddr`, `Coordinator`.`city` as `coordinatorCity`,
`Coordinator`.`phone` as `coordinatorPhone`, `Coordinator`.`email` as `coordinatorEmail`, `Coordinator`.`firstName`,
`Coordinator`.`lastName` ,
`Appointment`.`status`,
DATE_FORMAT(appointmentEndDate,  '%%Y-%%m-%%d %%T') as appointmentEndDate,
TIMESTAMPDIFF( MINUTE, appointmentStartDate , appointmentEndDate ) as appointmentDuration

FROM
`Coordinator` INNER JOIN `Appointment` ON `Coordinator`.`coordinatorId` = `Appointment`.`coordinatorId`
WHERE
`Appointment`.`demographicNo` = %s AND
`Appointment`.`appointmentStartDate` < CURDATE()
ORDER BY `Appointment`.`appointmentStartDate` DESC;
'''

#`Appointment`.`appointmentStartDate` >= CURDATE() AND `Appointment`.`appointmentStartDate` <= DATE_ADD(CURDATE(), INTERVAL 1 day)

getAppointmentTimesBetween = \
'''
SELECT
appointmentStartDate, appointmentEndDate,
DATE_FORMAT(appointmentStartDate, '%%H:%%i') as appointmentTime,
DAYOFWEEK(appointmentStartDate)-1 as dayOfWeek
FROM Appointment
WHERE appointmentStartDate >= %s AND DATE_FORMAT(appointmentStartDate,  '%%Y-%%m-%%d') <= %s
ORDER BY appointmentStartDate ASC;
'''


getAppointments = \
'''
select
caseId,
coordinatorId,
demographicNo,
name,
type,
DATE_FORMAT(appointmentStartDate,  '%%Y-%%m-%%dT%%T') as appointmentStartDate ,
resources,
location,
reason,
notes,
DATE_FORMAT(dateCreated,  '%%Y-%%m-%%dT%%T') as dateCreated ,
DATE_FORMAT(dateUpdated,  '%%Y-%%m-%%dT%%T') as dateUpdated
from Appointment
where demographicNo = %s
order by appointmentStartDate DESC
;
'''

getAppointmentWaiver = \
'''
select waiverPDF
from Appointments
where demographicNo = %s
;
'''





getDoctorOnCall = "select doctorId,name,email,cellPhone, DATE_FORMAT(onCallStartTime, '%Y-%m-%dT%TZ') as onCallStartTime , DATE_FORMAT(onCallEndTime, '%Y-%m-%dT%T') as onCallEndTime from Doctor where current=1 and archive=0"

getDoctors = "select doctorId,name,email,cellPhone,current as onCall, receiveEmail,receiveText from Doctor where archive=0 order by name"


getAdminCoordinators = "select email from Coordinator where admin='T'"

getDoctorByEmail = "select doctorId,name,email,cellPhone,current as onCall, receiveEmail,receiveText  from Doctor where email = %s and archive=0"

getDoctorById = "select doctorId,name,email,cellPhone,current as onCall, receiveEmail,receiveText, oscarProviderNo from Doctor where doctorId=%s and archive=0"

getDoctorByEmailNameCellPhone = "select doctorId,name,email,cellPhone, current as onCall, receiveEmail,receiveText from Doctor where email = %s and name = %s and cellPhone = %s and archive=0"

updateDoctor = \
'''
update Doctor set
name = %s ,
email = %s ,
cellPhone = %s,
oscarProviderNo = %s,
current = %s ,
archive=0 ,
receiveEmail = %s ,
receiveText = %s
where
doctorId = %s
'''



setDoctorOnCall = "update Doctor set current=1 where doctorId = %s"
setDoctorOnCallById = "update Doctor set current=%s where doctorId = %s"
setDoctorReceiveEmailById = "update Doctor set receiveEmail=%s where doctorId = %s"
setDoctorReceiveTextById = "update Doctor set receiveText=%s where doctorId = %s"

archiveAllDoctors = "update Doctor set archive=1"
unarchiveAllDoctors = "update Doctor set archive=0"
removeArchivedDoctors = 'delete from Doctor where archive=1'

deleteDoctor = 'delete from Doctor where doctorId=%s'

unsetAllDoctorOnCall = "update Doctor set current=0"

insertDoctor = \
'''

insert into Doctor
(
    name,
    email ,
    cellPhone,
    current,
    archive,
    receiveEmail,
    receiveText
)
values
(
    %s ,%s ,%s,%s,0,%s,%s
)
'''

getEmailsForAppointmentNotification = \
'''
(SELECT `email`	FROM `Doctor` WHERE `current` = 1 and receiveEmail = 'T')
UNION DISTINCT
(SELECT `email` FROM `Coordinator` WHERE `receivesWaiverEmails` = 'T');
'''

getEmailsForErrorMessage = \
'''
(SELECT `email` FROM `Coordinator` WHERE `receiveErrorEmails` = 'T');
'''


getCellPhoneForAppointmentNotification = \
'''
(SELECT REPLACE(`cellPhone`,' ','') FROM `Doctor` WHERE `current` = 1 and length(`cellPhone`)>= 9 and receiveText = 'T')
UNION DISTINCT
(SELECT REPLACE(`cellPhone`,' ','')	FROM `Coordinator` WHERE length(`cellPhone`)>= 9 and receiveAppointmentText = 'T');
'''


getProviderNumber = \
'''
(SELECT `oscarProviderNo` FROM `Doctor` WHERE `current` = 1);
'''

updateAppointmentStatus = \
'''
update Appointment set status = %s where caseId = %s
'''

