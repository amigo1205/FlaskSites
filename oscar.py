from log import log
import json
import datetime
import appExceptions as ae
from suds import WebFault
from suds.client import Client
from suds.sax.element import Element
from suds.sax.attribute import Attribute

#HOSTWWW = 'https://www.oscarhost.ca'
#HOST = "https://signup1.oscarhost.ca"
#INSTANCE = 'snapmd'
#USER = 'ywang'
#PASS = 'Dgi48a7p'
#PROVIDER = 999998

HOST = 'https://secure20.oscarhost.ca'
INSTANCE = 'clickmd'
USER = 'barinda'
PASS = 'Temp3895'
#PROVIDER = 999998
PROVIDER = 999998


def create_patient_obj():
    """Creates a blank demographicsTransfer document from the SOAP definition.

    The intended use for this object is to be a placeholder for the data we will send to OSCAR and
    the database. Since the WSDL requires this format, we may as well store it in that.

    Returns:
        blank demographicsTransfer object

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    try:
        demographicsClient = Client("%s/%s/ws/DemographicService?wsdl" % (HOST, INSTANCE))
        return demographicsClient.factory.create('demographicTransfer')
    except WebFault as we:
        log.exception(we)
        raise ConnectionRefusedError("There was a problem connecting to OSCAR when creating the patient object. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise


def create_case_obj():
    """Creates a blank appointmentTransfer document from the SOAP definition.

    The intended use for this object is to be a placeholder for the data we will send to OSCAR and
    the database. Since the WSDL requires this format, we may as well store it in that.

    Returns:
        blank appointmentTransfer object

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    try:
        scheduleClient = Client("%s/%s/ws/ScheduleService?wsdl" % (HOST, INSTANCE))
        return scheduleClient.factory.create('appointmentTransfer')
    except WebFault as we:
        log.exception(we)
        raise ConnectionRefusedError("There was a problem connecting to OSCAR when creating the patient object. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise


def add_patient_info(patient_obj):
    """Takes in a demographicsTransfer document and sends it off to OSCAR.

    Note: duplicate entries are allowed in OSCAR. Takes care of dummy fields.

    Args:
        patient_obj (demographicsTransfer): the patient object you wish to add to OSCAR.

    Returns:
        the demographic_num for the new patient entry

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    try:
        demographicsClient = Client("%s/%s/ws/DemographicService?wsdl" % (HOST, INSTANCE))
        demographicsClient.set_options(soapheaders=[login()])
        patient_obj.hsAlertCount = 0
        patient_obj.activeCount = 1
        return demographicsClient.service.addDemographic(patient_obj)
    except WebFault as we:
        log.exception(we)
        raise ConnectionRefusedError("There was a problem connecting to OSCAR when adding the patient. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise


def update_patient_info(demographic_num, patient_obj):
    """Takes in a demographicsTransfer document and replaces the OSCAR entry with the provided demographic_num

    Note: OSCAR will erase and replace fields with a null value if patient_obj does not explicitly define
        that field. To have values persist across updates, always pass in the modified original object.

    Args:
        demographic_num (int): the unique ID for the OSCAR patient demographic
        patient_obj (demographicsTransfer): the modified patient object you wish to send to OSCAR.

    Raises:
        BadDemographicNum: When the demographic_num is invalid
        Exception: All other uncaught errors

    """
    try:
        demographicsClient = Client("%s/%s/ws/DemographicService?wsdl" % (HOST, INSTANCE))
        demographicsClient.set_options(soapheaders=[login()])
        patient_obj.demographicNo = demographic_num
        return demographicsClient.service.updateDemographic(patient_obj)
    except WebFault as we:
        log.exception(we)
        raise ae.BadDemographicNum()
    except Exception as e:
        log.exception(e)
        raise


def find_patient(demo_num):
    """Takes in a health care number and initiates a search for the patient object.

    Args:
        health_care_number (str): the health care number associated with the patient

    Returns:
        a list of demographicsTransfer objects

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    try:
        demographicsClient = Client("%s/%s/ws/DemographicService?wsdl" % (HOST, INSTANCE))
        demographicsClient.set_options(soapheaders=[login()])
        return demographicsClient.service.getDemographic(demo_num)
    except WebFault as we:
        raise ConnectionRefusedError("There was a problem connecting to OSCAR when getting the patient. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise


def add_case_info(case_obj):
    """Adds a case to OSCAR by setting up a one-minute appointment.

    Note: takes care of dates and dummy fields

    Args:
        case_obj (appointmentTransfer): the case object you wish to add to OSCAR.

    Returns:
        OSCAR's appointment ID for the entry

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    try:
        scheduleClient = Client("%s/%s/ws/ScheduleService?wsdl" % (HOST, INSTANCE))
        scheduleClient.set_options(soapheaders=[login()])

        case_obj.appointmentStartDateTime = datetime.datetime.strptime(case_obj.appointmentStartDateTime, "%Y-%m-%d %H:%M:%S")
        case_obj.appointmentEndDateTime = datetime.datetime.strptime(case_obj.appointmentEndDateTime, "%Y-%m-%d %H:%M:%S")

        case_obj.programId = 0
        case_obj.status = "t"

        if case_obj.providerNo == 0:
            case_obj.providerNo = PROVIDER

        return scheduleClient.service.addAppointment(case_obj)
    except WebFault as we:
        raise ConnectionRefusedError("There was a problem connecting to OSCAR when getting the patient. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise

def get_case_info(case_id):
    """Gets a certain appointment given a case ID.

    Args:
        case_id (int): the case_id you wish to refer to.

    Returns:
        the appointmentTransfer object

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    try:
        scheduleClient = Client("%s/%s/ws/ScheduleService?wsdl" % (HOST, INSTANCE))
        scheduleClient.set_options(soapheaders=[login()])
        return scheduleClient.service.getAppointment(case_id)
    except WebFault as we:
        raise ConnectionRefusedError(
            "There was a problem connecting to OSCAR when getting the patient. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise


def update_case_info(case_obj):

    try:
        scheduleClient = Client("%s/%s/ws/ScheduleService?wsdl" % (HOST, INSTANCE))
        scheduleClient.set_options(soapheaders=[login()])
        scheduleClient.service.updateAppointment(case_obj)
    except WebFault as we:
        raise ConnectionRefusedError(
            "There was a problem connecting to OSCAR when getting the patient. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise




def submit_signature(pdf_filename, pdf_uri, oscarProviderNo):
    """Submits a signed document using its base64 representation.

    Args:
        pdf_filename (string): the file name. Will already have date prepended and '.pdf' appended.
        pdf_uri (string): the base64 string representation of the PDF.

    Returns:
        a boolean indicating success

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    try:
        providerNo = oscarProviderNo

        if oscarProviderNo == 0:
            providerNo = PROVIDER

        documentClient = Client("%s/%s/ws/DocumentService?wsdl" % (HOST, INSTANCE))
        documentClient.set_options(soapheaders=[login()])
        res = documentClient.service.addDocument(' - ' + pdf_filename + '.pdf', pdf_uri, providerNo, providerNo)
        return json.loads(res)['success'] is 1;
    except WebFault as we:
        raise ConnectionRefusedError(
            "There was a problem connecting to OSCAR when sending the waiver document. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise


def login():
    """Defines the security header required by the SOAP server.

    Before making any call to an OSCAR service, you must run set_options(soapheaders=[login()])
        on that service object. This authenticates us using a username and password.

    Returns:
        a SOAP element object representing a wsse:Security header element

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    try:
        loginService = Client("%s/%s/ws/LoginService?wsdl" % (HOST, INSTANCE))
        result = loginService.service.login(USER, PASS)

        security = Element('wsse:Security')
        security.attributes.append(Attribute('xmlns:wsse', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))
        auth = Element('wsse:UsernameToken')
        auth.attributes.append(Attribute('xmlns:wsu', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))
        auth.attributes.append(Attribute('wsu:Id', 'UsernameToken-1'))
        auth.append(Element('wsse:Username').setText(result["securityId"]))
        pw = Element('wsse:Password').setText(result["securityTokenKey"])
        pw.attributes.append(Attribute('Type', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'))
        auth.append(pw)
        security.append(auth)

        return security

    except WebFault as we:
        raise ConnectionRefusedError("There was a problem connecting to OSCAR when logging in. Server status: " + test_alive())
    except Exception as e:
        log.exception(e)
        raise


def test_alive():
    """ Tests if the SOAP server is alive.

    Returns:
        a status message

    Raises:
        ConnectionRefusedError: When the connection is refused (usually a firewall problem)
        Exception: All other uncaught errors

    """
    test = False
    try:
        testClient = Client("%s/%s/ws/SystemInfoWs?wsdl" % (HOST, INSTANCE))
        testClient.set_options(soapheaders=[login()])
        test = testClient.service.isAlive()
    except WebFault as we:
        raise ConnectionRefusedError("There was a problem connecting to OSCAR when testing the server.")
    except Exception as e:
        raise
    finally:
        return "%salive." % ('' if test == 'alive' else 'not ',)