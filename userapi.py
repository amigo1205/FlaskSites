import requests
import json
import pymysql.err as dberror
from config import app
import database as DB
from log import log
import queries
import hashlib
import appExceptions as ae
import random
import string
import smtplib
import datetime
import oscar
import eztexting
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email import encoders
from datetime import timedelta, time

from flask import Blueprint, request, Response, jsonify, session, render_template

userapi = Blueprint( 'userapi' , __name__ )

REGULAR_OFFICE_HOURS = False




def randomString(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                   for _ in range(length))

def setAppointmentRequestToken( token  ):
    try:
        (db,cursor,message) = DB.connect()
        if db == None:
            return None

        query = queries.setAppointmentRequestToken
        cursor.execute(query, (token, ))
        db.commit()

    except Exception as e:
        return None




@userapi.route('/signIn', methods=['POST'])
def signInPost(  ):
    try:
        (db,cursor,message) = DB.connect()
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        req = request.get_json()

        query = queries.getCoordinator
        cursor.execute(query,(req["email"],))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        cursor.close(); db.close();

        if len(results_dict) <= 0:
            return jsonify(ae.BadEmail().errDict()), ae.BadEmail().code

        # Check if the user has been activated.
        if results_dict[0]["status"] == "NOTACTIVATED":
            return jsonify(ae.NotActive().errDict()), ae.NotActive().code

        if results_dict[0]["status"] == "UNAUTHORIZED":
            return jsonify(ae.EmailUnauthorized().errDict()), ae.EmailUnauthorized().code

        hashedPassword = hashlib.sha256(req["password"].encode('utf-8')).hexdigest()
        if results_dict[0]["passwordHash"] != hashedPassword:
            return jsonify(ae.BadPassword().errDict()), ae.BadPassword().code

        # Set the session variable
        session["authid"] = results_dict[0]["coordinatorId"]
        session.modified = True

        res = Response()
        res.mimetype = "application/json"
        res.set_cookie("_cmd-email_", str(results_dict[0]["email"]))
        res.set_data(json.dumps({"success": True,
                                 "error": {"code": 200, "message": "OK"}}))

        results_dict = None
        return res


    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500




@userapi.route('/signUp', methods=['POST'])
def signUpPost(  ):
    try:
        req = request.get_json()


        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        # check if this email already exists
        query = queries.getCoordinator
        cursor.execute(query,(req["email"],))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        if len(results_dict) > 0 and results_dict[0]["status"] != "NOTACTIVATED":
            cursor.close(); db.close();
            return jsonify(ae.EmailAlreadyExists().errDict()), ae.EmailAlreadyExists().code

        email_activation_token = randomString(40)

        # if doesn't exist to create it
        query = queries.createCoordinatorRecord
        try:
            result = cursor.execute(query,(
            req["firstName"],
            req["lastName"],
            req["email"],
            req["organization"],
            req["province"],
            req["city"],
            req["postal"],
            req["address1"],
            req.get("address2"),
            req["phone"],
            req.get("fax"),
            email_activation_token
            ))
        except dberror.IntegrityError as e:
            return jsonify(ae.EmailAlreadyExists().errDict()), ae.EmailAlreadyExists().code

        # TODO remove the initial passwordHash (i.e. 3cff...) set to dataESP0419 that allows logging in before activation
        if result <= 0:
            return jsonify(ae.InsertProviderRecordFailed().errDict()), ae.InsertProviderRecordFailed().code

        db.commit()

        # now query for the newly added record to determine the provider_id key that was assigned by the database
        query = queries.getCoordinator
        cursor.execute(query,(req["email"],))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        cursor.close(); db.close();

        if len(results_dict) <= 0:
            return jsonify(ae.InsertProviderRecordFailed().errDict()), ae.InsertProviderRecordFailed().code
        coordinatorId = results_dict[0]["coordinatorId"]


        server = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"] )
        server.starttls()
        server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])


        activationLink = request.scheme + "://" + request.host + "/activate/" + str(coordinatorId) + "/" + email_activation_token
        msg = MIMEMultipart()
        msg['Subject'] = "Welcome to ClickMD!"
        msg['From'] = app.config["MAIL_USERNAME"]
        msg['To'] = req["email"]

        msg.attach( MIMEText( render_template('emails/newCoordinatorActivation.html', coordinator=req , activationLink=activationLink , user_app_name=app.config["USER_APP_NAME"] ),'html'))
        msgAsString = msg.as_string()

        server.sendmail(app.config["MAIL_USERNAME"], req["email"], msgAsString )
        server.quit()

        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" })



    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500



@userapi.route('/resetPassword', methods=['POST'])
def resetPasswordPost(  ):
    try:
        req = request.get_json()


        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        # check if this email exists
        query = queries.getCoordinator
        cursor.execute(query,(req["email"],))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        if len(results_dict) is 0:
            cursor.close(); db.close()
            return jsonify(ae.BadEmail().errDict()), ae.BadEmail().code
        elif results_dict[0]["status"] != "ACTIVE" and results_dict[0]["status"] != "UNAUTHORIZED":
            cursor.close(); db.close();
            return jsonify(ae.BadEmailResetPassword().errDict()), ae.BadEmailResetPassword().code

        email_activation_token = randomString(40)

        # if doesn't exist to create it
        query = queries.updateCoordinatorEmailActivation

        result = cursor.execute(query,(
        email_activation_token,
        req["email"]
        ))

        db.commit()

        # now query for the newly added record to determine the provider_id key that was assigned by the database
        query = queries.getCoordinator
        cursor.execute(query,(req["email"],))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        cursor.close(); db.close();

        if len(results_dict) <= 0:
            return jsonify(ae.InsertProviderRecordFailed().errDict()), ae.InsertProviderRecordFailed().code
        coordinatorId = results_dict[0]["coordinatorId"]


        server = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"] )
        server.starttls()
        server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])


        activationLink = request.scheme + "://" + request.host + "/resetpassword/" + str(coordinatorId) + "/" + email_activation_token
        msg = MIMEMultipart()
        msg['Subject'] = app.config["USER_APP_NAME"] + " Password Reset Request"
        msg['From'] = app.config["MAIL_USERNAME"]
        msg['To'] = req["email"]

        msg.attach( MIMEText( render_template('emails/resetCoordinatorPassword.html', coordinator=results_dict[0] , activationLink=activationLink , user_app_name=app.config["USER_APP_NAME"] ),'html'))
        msgAsString = msg.as_string()

        server.sendmail(app.config["MAIL_USERNAME"], req["email"], msgAsString )
        server.quit()

        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" })



    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500



@userapi.route('/getCoordinatorData', methods=['POST'])
def getCoordinatorDataPost():

    if 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()
        coordinator_email = req["email"]

        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        query = queries.getCoordinator
        cursor.execute(query,(coordinator_email,))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        cursor.close(); db.close();

        if len(results_dict) <= 0 :
            return jsonify(ae.BadEmail().errDict()), ae.BadEmail().code

        # If the session doesn't match what comes back from the database, they are trying to spoof their session.
        if results_dict[0]["coordinatorId"] != session['authid']:
            res = Response(json.dumps(ae.BadCookies().errDict()), status=ae.BadCookies().code)
            res.set_cookie("_cmd-email_", expires=0)
            session.clear()
            return res

        # take sensitive attributes out of the client record
        del results_dict[0]["emailActivationToken"]
        del results_dict[0]["emailActivationExpiry"]
        del results_dict[0]["resetPasswordToken"]
        del results_dict[0]["resetPasswordExpiry"]
        del results_dict[0]["passwordHash"]

        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" },
                        data = results_dict[0])

    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e)}), 500

@userapi.route('/validateActivation', methods=['POST'])
def validateActivationPost():

    try:
        req = request.get_json()
        coordinatorId = req["coordinatorId"]
        activation = req['emailActivation']

        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        query = queries.getActivationDetails
        cursor.execute(query,(coordinatorId,))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        cursor.close(); db.close();

        if len(results_dict) <= 0:
            return jsonify(ae.BadProviderID().errDict()), ae.BadProviderID().code

        # User has no reason to request activation if already active.
        if results_dict[0]['status'] != "NOTACTIVATED":
            return jsonify(ae.BadActivation().errDict()), ae.BadActivation().code

        # Verifying the request
        if results_dict[0]['emailActivationToken'] != activation:
            return jsonify(ae.BadActivationKey().errDict()), ae.BadActivationKey().code
        if results_dict[0]['emailActivationExpiry'] < datetime.datetime.now():
            return jsonify(ae.ExpiredActivationKey().errDict()), ae.ExpiredActivationKey().code

        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" })

    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e)}), 500

#curl -H "Content-Type: application/json" -X POST -d '{"password":"dataESP0419"}' http://127.0.0.1:8001/activate

@userapi.route('/resetPasswordActivation', methods=['POST'])
def resetPasswordActivationPost():

    # TODO If user is already logged in?

    try:
        req = request.get_json()
        coordinatorId = req["coordinatorId"]
        activation = req['emailActivation']

        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        query = queries.getActivationDetails
        cursor.execute(query,(coordinatorId,))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        cursor.close(); db.close();

        if len(results_dict) <= 0:
            return jsonify(ae.BadProviderID().errDict()), ae.BadProviderID().code

        # User has no reason to request activation if already active.
        if results_dict[0]['status'] != "ACTIVE" and results_dict[0]['status'] != "UNAUTHORIZED":
            return jsonify(ae.BadActivationKey().errDict()), ae.BadActivationKey().code

        # Verifying the request
        if results_dict[0]['emailActivationToken'] != activation:
            return jsonify(ae.BadActivationKey().errDict()), ae.BadActivationKey().code
        if results_dict[0]['emailActivationExpiry'] < datetime.datetime.now():
            return jsonify(ae.ExpiredActivationKey().errDict()), ae.ExpiredActivationKey().code

        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" },
                        data = {'status': results_dict[0]['status']})

    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e)}), 500

#curl -H "Content-Type: application/json" -X POST -d '{"password":"dataESP0419"}' http://127.0.0.1:8001/activate

@userapi.route('/activate', methods=['POST'])
def activateAccountPost(  ):
    try:
        req = request.get_json()
        hashedPassword = hashlib.sha256(req["password"].encode('utf-8')).hexdigest()
        coordinatorId = req['coordinatorId']
        activation = req['emailActivation']


        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        query = queries.getActivationDetails
        cursor.execute(query, (coordinatorId,))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        # Verifying the request again
        if results_dict[0]['emailActivationToken'] != activation:
            return jsonify(ae.BadActivationKey().errDict()), ae.BadActivationKey().code
        if results_dict[0]['emailActivationExpiry'] < datetime.datetime.now():
            return jsonify(ae.ExpiredActivationKey().errDict()), ae.ExpiredActivationKey().code

        query = queries.getActivationDetails
        cursor.execute(query,(coordinatorId,))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        # This SHOULD not happen.
        if len(results_dict) <= 0:
            cursor.close(); db.close();
            return jsonify(ae.BadProviderID().errDict()), ae.BadProviderID().code

        query = queries.setCoordinatorPassword
        result = cursor.execute(query, (hashedPassword, coordinatorId))
        db.commit()

        if result <= 0:
            return jsonify(ae.SetPasswordFailed().errDict()), ae.SetPasswordFailed().code


        query = queries.getAdminCoordinators
        cursor.execute(query)
        query_results_admins = cursor.fetchall()
        results_dict_admins = [qr[0] for qr in query_results_admins]


        cursor.close(); db.close();

        server = smtplib.SMTP(app.config["MAIL_SERVER"],  app.config["MAIL_PORT"] )
        server.starttls()
        server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])


        msg = MIMEMultipart()
        msg['Subject'] = "ClickMD Account Authorization Request"
        msg['From'] = app.config["MAIL_USERNAME"]
        msg['To'] = ", ".join(results_dict_admins)

        activationLink = request.scheme + "://" + request.host + "/authorization"

        msg.attach( MIMEText( render_template('emails/authorizationRequest.html', activationLink=activationLink , coordinator=results_dict[0] , user_app_name=app.config["USER_APP_NAME"] ),'html'))
        msgAsString = msg.as_string()

        server.sendmail(app.config["MAIL_USERNAME"], results_dict_admins, msgAsString )
        server.quit()


        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" })


    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500

@userapi.route('/resetPasswordActivate', methods=['POST'])
def resetPasswordActivateAccountPost(  ):
    try:
        req = request.get_json()
        hashedPassword = hashlib.sha256(req["password"].encode('utf-8')).hexdigest()
        coordinatorId = req['coordinatorId']
        activation = req['emailActivation']

        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500


        query = queries.getActivationDetails
        cursor.execute(query,(coordinatorId,))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        # This SHOULD not happen.
        if len(results_dict) <= 0:
            cursor.close(); db.close();
            return jsonify(ae.BadProviderID().errDict()), ae.BadProviderID().code

        # Verifying the request again
        if results_dict[0]['emailActivationToken'] != activation:
            return jsonify(ae.BadActivationKey().errDict()), ae.BadActivationKey().code
        if results_dict[0]['emailActivationExpiry'] < datetime.datetime.now():
            return jsonify(ae.ExpiredActivationKey().errDict()), ae.ExpiredActivationKey().code



        query = queries.resetCoordinatorPassword
        result = cursor.execute(query, (hashedPassword, coordinatorId))
        db.commit()

        if result <= 0:
            return jsonify(ae.SetPasswordFailed().errDict()), ae.SetPasswordFailed().code

        cursor.close(); db.close();

        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" })


    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500


@userapi.route('/getDemographicByHIN', methods=['POST'])
def getDemographicPatientByHIN():
    if 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()
        hin = req['hin']
        ver = req['ver']

        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        query = queries.getDemographicInfo
        result = cursor.execute(query, (hin, ver))
        query_results = cursor.fetchall()
        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]




        if len(results_dict) <= 0:
            demographicRecord = {
                "hin":hin,
                "ver":ver ,
                "effDate":"",
                "hcType":"",
                "firstName":""             ,
                "lastName":""     ,
                "officialLanguage":""     ,
                "sex":""   ,
                "email":""      ,
                "phone":""      ,
                "phone2":""      ,
                "address":""      ,
                "city":""      ,
                "province":""      ,
                "postal":"" ,
                "dateOfBirth":""    ,
                "monthOfBirth":""    ,
                "yearOfBirth":""    ,
                "dateCreated":""    ,
                "notes":""       ,
                "spokenLanguage":""         ,
                "demographicNo":""
            }


            return jsonify( success = False,data=demographicRecord,
                            error = {'code': 200, 'message': req['hin'] + " was not found." })


        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" },
                        data = results_dict[0])


    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500




@userapi.route('/saveDemographicPost', methods=['POST'])
def saveDemographicPost(  ):
    if 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()

        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500


        query = queries.getDemographicInfo
        cursor.execute(query,(req['hin'],req['ver']))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        # Record found. Update OSCAR.
        if len(results_dict) > 0:
            try:
                demo_obj = oscar.find_patient(results_dict[0]['demographicNo'])
                demo_num = results_dict[0]['demographicNo']
                if fill_demographic_object(demo_obj, req) is None:
                    cursor.close(); db.close();
                    jsonify(ae.BadForm().errDict()), ae.BadForm().code
                oscar.update_patient_info(results_dict[0]['demographicNo'],demo_obj)
            except Exception as e:
                cursor.close(); db.close();
                return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code

            # Update database
            query = queries.updateDemographicRecord
            result = cursor.execute(query, (
                req['effDate'],
                req['hcType'],
                req['firstName'],
                req['lastName'],
                req['officialLanguage'],
                req['sex'],
                req['email'],
                req['phone'],
                req.get('phone2'),
                req['address'],
                req['city'],
                req['province'],
                req['postal'],
                req['dateOfBirth'],
                req['monthOfBirth'],
                req['yearOfBirth'],
                req.get('notes'),
                req['spokenLanguage'],
                req['hin'],
                req['ver']

            ))
            db.commit()
            if result < 0:
                return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code

            return jsonify( success = True,
                            error = {'code': 200, 'message': "OK" },
                             data = { "demographicNo": demo_num })

        # No records found. Send to OSCAR.
        else:
            demo_obj = oscar.create_patient_obj()
            if fill_demographic_object(demo_obj, req) is None:
                cursor.close(); db.close();
                return jsonify(ae.BadForm().errDict()), ae.BadForm().code
            try:
                demo_num = oscar.add_patient_info(demo_obj)
            except Exception as e:
                cursor.close(); db.close();
                return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code

            # If that succeeded, we can send to the database.
            query = queries.insertDemographicRecord
            result = cursor.execute(query, (
                req['hin'],
                req['ver'],
                req['effDate'],
                req['province'],
                req['firstName'],
                req['lastName'],
                req['officialLanguage'],
                req['sex'],
                req['email'],
                req['phone'],
                req.get('phone2'),
                req['address'],
                req['city'],
                req['hcType'],
                req['postal'],
                req['dateOfBirth'],
                req['monthOfBirth'],
                req['yearOfBirth'],
                req.get('notes'),
                demo_num,
                req['spokenLanguage']
            ))
            db.commit()
            if result <= 0:
                return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code

            return jsonify( success = True,
                            error = {'code': 200, 'message': "OK" },
                            data = { "demographicNo": demo_num })


    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500


def fill_demographic_object(obj, info):
    '''Given a dict of form values, populates (or replaces) the values in the demographic object.

    Args:
        obj (demographicTransfer): the demographic object that holds the OSCAR values
        info (dict): the requested changes to be made to obj

    Returns:
        the modified obj, or None if an error occurred.
    '''
    try:
        obj['hin']                  = info['hin']
        obj['ver']                  = info['ver']
        obj['hcType']               = info['hcType']
        obj['effDate']              = info['effDate']
        obj['firstName']            = info['firstName']
        obj['lastName']             = info['lastName']
        obj['officialLanguage']     = info['officialLanguage']
        obj['sex']                  = info['sex']
        obj['email']                = info['email']
        obj['phone']                = info['phone']
        obj['phone2']               = info.get('phone2')
        obj['address']              = info['address']
        obj['province']             = info['province']
        obj['postal']               = info['postal']
        obj['dateOfBirth']          = info['dateOfBirth']
        obj['monthOfBirth']         = info['monthOfBirth']
        obj['yearOfBirth']          = info['yearOfBirth']
        obj['spokenLanguage']       = info.get('spokenLanguage')
        return obj
    except Exception as e:
        log.exception(str(e))
        return None


@userapi.route('/addAppointmentRecord', methods=['POST'])
def addAppointmentRecord():
    if 'appointmentRequest' not in session:
        return jsonify(ae.AccessDenied().errDict()), ae.AccessDenied().code
    try:
        req = request.get_json()

        #log.info( req )
        # to manually test adding an appointment in the past
        #req['appointmentStartDate'] = "2016-10-02 10:20:00"
        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500


        query = queries.getAppointmentRequestToken
        cursor.execute(query, ( session['appointmentRequest'], ))
        query_results = cursor.fetchall()
        if len(query_results) == 0:
            return jsonify(ae.AccessDenied().errDict()), ae.AccessDenied().code

        appointmentRequestToken = query_results[0][0]

        # if not session['appointmentRequest'] == appointmentRequestToken:

        query = queries.getDemographicInfo
        cursor.execute(query,(req['hin'],req['ver']))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]


        # Record found. Update OSCAR.
        if len(results_dict) > 0:
            try:
                req['demographicNo'] = results_dict[0]['demographicNo']
                demo_obj = oscar.find_patient(results_dict[0]['demographicNo'])
                demo_num = results_dict[0]['demographicNo']
                if fill_demographic_object(demo_obj, req) is None:
                    cursor.close(); db.close();
                    jsonify(ae.BadForm().errDict()), ae.BadForm().code
                oscar.update_patient_info(results_dict[0]['demographicNo'],demo_obj)
            except Exception as e:
                cursor.close(); db.close();
                return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code

            # Update database
            query = queries.updateDemographicRecord
            result = cursor.execute(query, (
                req['effDate'],
                req['hcType'],
                req['firstName'],
                req['lastName'],
                req['officialLanguage'],
                req['sex'],
                req['email'],
                req['phone'],
                req.get('phone2'),
                req['address'],
                req['city'],
                req['province'],
                req['postal'],
                req['dateOfBirth'],
                req['monthOfBirth'],
                req['yearOfBirth'],
                req.get('notes'),
                req['spokenLanguage'],
                req['hin'],
                req['ver']

            ))
            db.commit()
            if result < 0:
                return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code

        # No records found. Send to OSCAR.
        else:
            demo_obj = oscar.create_patient_obj()
            if fill_demographic_object(demo_obj, req) is None:
                cursor.close(); db.close();
                return jsonify(ae.BadForm().errDict()), ae.BadForm().code
            try:
                demo_num = oscar.add_patient_info(demo_obj)
            except Exception as e:
                cursor.close(); db.close();
                return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code
            req['demographicNo'] = demo_num
            # If that succeeded, we can send to the database.
            query = queries.insertDemographicRecord
            result = cursor.execute(query, (
                req['hin'],
                req['ver'],
                req['effDate'],
                req['province'],
                req['firstName'],
                req['lastName'],
                req['officialLanguage'],
                req['sex'],
                req['email'],
                req['phone'],
                req.get('phone2'),
                req['address'],
                req['city'],
                req['hcType'],
                req['postal'],
                req['dateOfBirth'],
                req['monthOfBirth'],
                req['yearOfBirth'],
                req.get('notes'),
                demo_num,
                req['spokenLanguage']
            ))
            db.commit()
            if result <= 0:
                return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code


        case_obj = oscar.create_case_obj()
        case_obj['reason'] = req['reason']
        case_obj['notes'] = req.get('notes')
        case_obj['name'] = req['name']
        case_obj['demographicNo'] = demo_num
        if not 'waiverPDF' in req:
            req['waiverPDF'] = ""
        if not 'appointmentStartDate' in req:
            req['appointmentStartDate'] = datetime.datetime.now().isoformat()
            log.info( "startdate not given so using current datetime.now() req['appointmentStartDate'] = " + req['appointmentStartDate'])
        else:
            log.info( "req[appointmentStartDate] = " + req['appointmentStartDate'] )

        req['appointmentStartDate'] = req['appointmentStartDate'].replace( "T" , " ")
        req['appointmentStartDate'] = req['appointmentStartDate'].split( ".")[0]

        startDateTimeTokens = req['appointmentStartDate'].split(":")
        if len(startDateTimeTokens) != 3:
            req['appointmentStartDate'] = datetime.datetime.now().isoformat()
            log.info( "startdate not valid so using current datetime.now() req['appointmentStartDate'] = " + req['appointmentStartDate'])

        #ensure there are no seconds, messes up the appointment duration calculation
        req['appointmentStartDate'] = startDateTimeTokens[0] + ":" + startDateTimeTokens[1] + ":00"
        startDateTime = datetime.datetime.strptime(req['appointmentStartDate'], "%Y-%m-%d %H:%M:%S")
        endDateTime = startDateTime + timedelta( minutes= 20 );



        req['appointmentEndDate'] = endDateTime.strftime( "%Y-%m-%d %H:%M:00" )

        case_obj['appointmentStartDateTime'] = req['appointmentStartDate']
        case_obj['appointmentEndDateTime'] = req['appointmentEndDate']

        query = queries.getProviderNumber
        cursor.execute(query)
        results_dict = list(map(lambda x: x[0], cursor.fetchall()))
        oscarProviderNo = results_dict[0]

        case_obj['providerNo'] = oscarProviderNo


        log.info( "case_obj = " + str(case_obj) )

        try:
            case_id = oscar.add_case_info(case_obj)
        except Exception as e:
            cursor.close(); db.close();
            return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code



        query = queries.insertAppointmentInfo
        cursor.execute(query, (
            case_id,
            req['coordinatorId'],
            req['demographicNo'],
            req['appointmentStartDate'],
            req['reason'],
            req.get('notes'),
            req['name'],
            req['waiverPDF'],
            req['appointmentEndDate']
        ))
        db.commit()

        query = queries.clearAppointmentRequestToken
        cursor.execute(query, (appointmentRequestToken,))
        db.commit()

        attachedPDFFile = MIMEApplication(req['waiverPDF'], _subtype="pdf")
        attachedPDFFile.add_header('Content-Disposition', 'attachment', filename="waiver.pdf")
        encoders.encode_base64(attachedPDFFile)

        query = queries.getEmailsForAppointmentNotification
        cursor.execute(query)
        results_dict = list(map(lambda x: x[0], cursor.fetchall()))

        if len(results_dict) > 0 and not app.config['DEBUG']:
            # send email to designated administratior if NOT in debug mode
            # send email to on-call doctor if NOT in debug mode
            server = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"] )
            server.starttls()
            server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])

            msg = MIMEMultipart()
            msg['Subject'] = app.config["USER_APP_NAME"] + " Appointment and Signed Waiver"
            msg['From'] = app.config["MAIL_USERNAME"]
            msg['To'] = results_dict[0]

            msg.attach( MIMEText( render_template('emails/signedWaiver.html', patient=req , user_app_name=app.config["USER_APP_NAME"] ),'html'))
            msg.attach(attachedPDFFile)

            msgAsString = msg.as_string()
            server.sendmail(app.config["MAIL_USERNAME"], results_dict, msgAsString )

            server.quit()



        PDFContentEncoded = attachedPDFFile._payload
        # PDFContentEncoded is the signedWaiver that can get sent to Oscar
        oscar.submit_signature("waiver_" + req["firstName"] + req["lastName"], PDFContentEncoded.replace('\n', ''), oscarProviderNo)

        query = queries.getCellPhoneForAppointmentNotification
        cursor.execute(query)
        textRecipients = ""
        for phone in cursor.fetchall():
            textRecipients = textRecipients + "&PhoneNumbers[]=" + phone[0]

        textMessage = ("%s\n%s\n%s\nCheck your OSCAR Schedule" % ( req['name'][:30] , req['appointmentStartDate'] , req['reason']))
        textSubject = "ClickMD Appt"

        eztexting.send_sms(textRecipients, textSubject , textMessage)

        cursor.close();
        db.close();

        return jsonify(success=True,
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500


#curl -H "Content-Type: application/json" -X POST  -d '{"demographicNo":"135"}' http://127.0.0.1:8001/getAppointments


@userapi.route('/getAppointments', methods=['POST'])
def getAppointments():
    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()
        demographicNo = req['demographicNo']

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.getAppointments
        cursor.execute(query, ( demographicNo,) );
        query_results = cursor.fetchall()

        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        return jsonify(success=True, data=results_dict ,
                       error={'code': 200, 'message': "OK"})



    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500

#curl -H "Content-Type: application/json" -X POST  -d '{"demographicNo":"135"}' http://127.0.0.1:8001/getCurrentAppointments


@userapi.route('/getCurrentAppointments', methods=['POST'])
def getCurrentAppointments():
    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()
        demographicNo = req['demographicNo']


        (db, cursor, message) = DB.connect();
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.getCurrentAppointments
        cursor.execute(query, ( demographicNo,) );
        query_results = cursor.fetchall()


        results_dict_current = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        query = queries.getPastAppointments
        cursor.execute(query, ( demographicNo,) );
        query_results = cursor.fetchall()

        cursor.close(); db.close();

        results_dict_past = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        return jsonify(success=True,
                       error={'code': 200, 'message': "OK"},
                       data={'currentAppointments':results_dict_current , 'pastAppointments':results_dict_past } )

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500



#getISODateValue = {
#    "Monday": 1,
#    "Tuesday": 2,
#    "Wednesday": 3,
#    "Thursday": 4,
#    "Friday": 5,
#}

#getISODateValue = {
#    "Monday": 1,
#    "Tuesday": 2,
#    "Wednesday": 3,
#    "Thursday": 4,
#    "Friday": 5,
#    'Saturday':6,
#    'Sunday':7
#}


@userapi.route('/getEarliestAppointment', methods=['POST'])
def getEarliestAppointment():

    if not app.config['DEBUG'] and 'appointmentRequest' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()
        dateTimeNow = req['date']

        today = datetime.datetime.today().date()

        if REGULAR_OFFICE_HOURS:
            # if this is a weekend, and using 5 day week, go to the next week
            #if today.isoweekday() > 5:
            #    firstDayInWeek = today - timedelta(days=today.isoweekday() - 1-7)
            #    lastDayInWeek = today + timedelta(days=5 - today.isoweekday()+7)
            #else:
            firstDayInWeek = today - timedelta(days=today.isoweekday() - 1)
            lastDayInWeek = today + timedelta(days=5 - today.isoweekday())
        else:
                firstDayInWeek = today - timedelta(days=today.isoweekday() - 1)
                lastDayInWeek = today + timedelta(days=5 - today.isoweekday())

#        lastDayInWeek = today + timedelta(days=7 - today.isoweekday())

        date = None
        while True:
            table = getAppointmentTable(firstDayInWeek, lastDayInWeek, dateTimeNow )
            # for 1 to number of days in week
            if REGULAR_OFFICE_HOURS:
                daysInWeek = 5
            else:
                daysInWeek = 7

            for i in range(0, daysInWeek ):
                for slot in table['appointments']:
                    if slot['available'][i] is 1:
                        tokens = slot['time'].split(':')
                        result = datetime.datetime.combine(firstDayInWeek + timedelta(days=i), time(int(tokens[0]), int(tokens[1])))
                        return jsonify(success=True,
                                       data=str(result),
                                       error={'code': 200, 'message': "OK"})

            # Failed to find open slot. Next week:
            firstDayInWeek += timedelta(days=7)
            lastDayInWeek += timedelta(days=7)
            log.info( "failed to find open slot. try firstDayInWeek = " +str( firstDayInWeek) + " lastDayInWeek " + str(lastDayInWeek) )

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500



#curl -H "Content-Type: application/json" -X POST  -d '{"date":"2016-11-11 11:00:00"}' http://127.0.0.1:8001/getAvailableAppointmentTimes



@userapi.route('/getAvailableAppointmentTimes', methods=['POST'])
def getAvailableAppointmentTimes():
    if not app.config['DEBUG'] and 'appointmentRequest' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()
        dateTimeNow = req['date']
        try:
            dayInWeek = datetime.datetime.strptime(req['date'], "%Y-%m-%d %H:%M:%S").date()
        except Exception as e:
            dayInWeek = datetime.datetime.strptime(req['date'], "%Y-%m-%d").date()

        firstDayInWeek = dayInWeek - timedelta( days= dayInWeek.isoweekday()-1 )
        if REGULAR_OFFICE_HOURS:
            lastDayInWeek = dayInWeek + timedelta( days= 5-dayInWeek.isoweekday() )
        else:
            lastDayInWeek = dayInWeek + timedelta( days= 7-dayInWeek.isoweekday() )


        availableAppointmentTimes = getAppointmentTable(firstDayInWeek, lastDayInWeek, dateTimeNow )

        return jsonify(success=True, data=availableAppointmentTimes,
                       error={'code': 200, 'message': "OK"})


    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500



def getAppointmentTable(firstDay, lastDay, dateTimeNow ):

    if dateTimeNow is None:
        dateTimeNow = datetime.datetime.now();
    else:
        dateTimeNow = datetime.datetime.strptime(dateTimeNow,  "%Y-%m-%d %H:%M:%S")


    (db, cursor, message) = DB.connect();
    if db == None:
        return jsonify(success=False,
                       error={'code': 500, 'message': message}), 500

    query = queries.getAppointmentTimesBetween
    cursor.execute(query, (firstDay, lastDay))
    query_results = cursor.fetchall()

    results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
    cursor.close();
    db.close()


    if REGULAR_OFFICE_HOURS:
        daysInWeek = 5;
        startTime = datetime.timedelta(hours=10, minutes=0)
        endTime = datetime.timedelta(hours=16, minutes=0)
        interval = 1200  # seconds = 20 minutes
        dayList = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday' ]
        timesList = list(map(lambda secondsDelta: startTime + timedelta(seconds=secondsDelta), range(0, int((endTime - startTime).seconds), interval)))
        availableAppointmentTimes = {
        "weekOfDate": str(firstDay),
        "dayList": dayList,
        "appointments": list(map(lambda time: {'time': str(time), 'available': [1,1,1,1,1]}, timesList))
    }
    else:
        daysInWeek = 7;
        startTime = datetime.timedelta(hours=00, minutes=0)
        endTime = datetime.timedelta(hours=23, minutes=59)
        interval = 1200  # seconds = 20 minutes
        dayList = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' , 'Sunday' ]
        # if end time is 24 hours, use this rather than end time since 24 hours becomes 1 day 0 minutes and messes everything up
        timesList = list(map(lambda secondsDelta: startTime + timedelta(seconds=secondsDelta),
                         range(0, int((endTime - startTime).seconds), interval)))
        availableAppointmentTimes = {
        "weekOfDate": str(firstDay),
        "dayList": dayList,
        "appointments": list(map(lambda time: {'time': str(time), 'available': [1,1,1,1,1,1,1]}, timesList))
    }


    #availableList = list(map(
    #    lambda day:
    #    0 if firstDay + timedelta(days=getISODateValue[day] - 1) < datetime.datetime.today().date() else 1,
    #    dayList))


    #    "appointments": list(map(lambda time: {'time': str(time), 'available': availableList.copy()}, timesList))

    for i in range(0, len(results_dict) ):
        setAvailableAppointment(availableAppointmentTimes["appointments"],
                                int(results_dict[i]['dayOfWeek']),
                                mapTimeToAppointment(results_dict[i]['appointmentTime']),
                                0)

    #for slot in availableAppointmentTimes["appointments"]:
    #    if (datetime.datetime.strptime(slot["time"], "%H:%M:%S") + timedelta(
    #            seconds=300)).time() < datetime.datetime.now().time():
    #        slot["available"][datetime.datetime.now().isoweekday() - 1] = 0

    for slot in availableAppointmentTimes["appointments"]:
    # TODO enviroments vars to configure available days and time in schedule
        for day in range(0,daysInWeek):
            appointmentDateTimeString = availableAppointmentTimes["weekOfDate"] + " " + slot["time"];
            appointmentDateTime = datetime.datetime.strptime(appointmentDateTimeString,  "%Y-%m-%d %H:%M:%S");
            appointmentDateTime = appointmentDateTime  + datetime.timedelta(days=day) + datetime.timedelta( seconds=300 )
            if appointmentDateTime < dateTimeNow:
                slot["available"][day] = 0


    return availableAppointmentTimes


def mapTimeToAppointment( t ):
    try:
        tokens = t.split( ":" )
        newMinutes = int(int(tokens[1])/20)*20
        return tokens[0]+":"+"%02d"%newMinutes+":00"

    except Exception as e:
        return t


def setAvailableAppointment( appointments , isoweekday , t , value ):
    t2 = ""
    if t[0] == '0':
        t2 = t[1:]

    for appointmentTime in appointments:
        if appointmentTime["time"] == t or appointmentTime["time"] == t2:
            appointmentTime['available'][isoweekday-1] = value
            break;


@userapi.route('/getAdvertisingCoordinators')
def getAdvertisingCoordinators():
    try:
        (db, cursor, message) = DB.connect();
        if db is None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.getAdvertisingCoordinators
        cursor.execute(query)
        query_results = cursor.fetchall()
        cursor.close(); db.close()

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        return jsonify(success=True,
                       error={'code': 200, 'message': "OK"},
                       data=results_dict)

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500

@userapi.route('/getUnauthorizedCoordinators', methods=['POST'])
def getUnauthorizedCoordinators():
    if 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()

        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        query = queries.getUnauthorizedCoordinators
        result = cursor.execute(query)
        query_results = cursor.fetchall()
        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]




        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" },
                        data = results_dict)


    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500



@userapi.route('/setAuthorizedCoordinator', methods=['POST'])
def setAuthorizedCoordinator():
    if 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:
        req = request.get_json()

        (db,cursor,message) = DB.connect();
        if db == None:
            return jsonify( success = False,
                            error = {'code': 500, 'message': message }), 500

        query = queries.setAuthorizedCoordinator
        result = cursor.execute(query ,( req["coordinatorId"],) )
        db.commit()

        query = queries.getCoordinatorById
        cursor.execute(query,(req["coordinatorId"],))
        query_results = cursor.fetchall()
        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]


        cursor.close(); db.close();



        server = smtplib.SMTP(app.config["MAIL_SERVER"],  app.config["MAIL_PORT"] )
        server.starttls()
        server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])


        msg = MIMEMultipart()
        msg['Subject'] = "ClickMD Account Authorization Success"
        msg['From'] = app.config["MAIL_USERNAME"]
        msg['To'] = results_dict[0]['email']

        activationLink = request.scheme + "://" + request.host + "/login"

        msg.attach( MIMEText( render_template('emails/authorizationSuccess.html', activationLink=activationLink , coordinator=results_dict[0] , user_app_name=app.config["USER_APP_NAME"] ),'html'))
        msgAsString = msg.as_string()

        server.sendmail(app.config["MAIL_USERNAME"], results_dict[0]['email'], msgAsString )
        server.quit()



        return jsonify( success = True,
                        error = {'code': 200, 'message': "OK" })


    except Exception as e:
        log.exception( str(e) )
        return jsonify( success = False,
                        error = {'code': 500, 'message': str(e) }), 500

#curl -H "Content-Type: application/json" -X GET http://127.0.0.1:8001/getCoordinators

@userapi.route('/getCoordinators', methods=['GET'])
def getCoordinators():
    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.getCoordinators
        cursor.execute(query)
        query_results = cursor.fetchall()

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True,  data=results_dict,
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500





#curl -H "Content-Type: application/json" -X GET http://127.0.0.1:8001/getDoctorOnCall

@userapi.route('/getDoctorOnCall', methods=['GET'])
def getDoctorOnCall():
    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.getDoctorOnCall
        cursor.execute(query)
        query_results = cursor.fetchall()
        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True,  data=results_dict,
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500

@userapi.route('/updateCoordinator', methods=['POST'])
def updatecoordinator():

    req = request.get_json()
    coordinatorFirstName = req['firstName']
    coordinatorLastName = req['lastName']
    coordinatorEmail = req['email']
    coordinatorOrganization = req['organization']
    coordinatorProvince = req['province']
    coordinatorCity = req['city']
    coordinatorPostal = req['postal']
    coordinatorAddress1 = req['address1']
    coordinatorAddress2 = req.get("address2")
    coordinatorPhone = req["phone"]
    coordinatorFax = req.get("fax")
    coordinatorStatus = req['status']
    coordinatorReceiveErrorEmails = req['receiveErrorEmails']
    coordinatorReceiveErrorText = req['receiveErrorText']
    coordinatorIncludeInProviderList = req['includeInProviderList']
    coordinatorReceivesWaiverEmails = req['receivesWaiverEmails']
    coordinatorReceiveAppointmentText = req['receiveAppointmentText']
    coordinatorCellPhone = req.get('cellPhone')
    coordinatorCoordinatorId = req['coordinatorId']
    coordinatorAdmin = req['admin']

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500


        query = queries.updateCoordinator
        cursor.execute(query, (coordinatorFirstName, coordinatorLastName, coordinatorEmail, coordinatorOrganization,
                               coordinatorProvince, coordinatorCity, coordinatorPostal, coordinatorAddress1, coordinatorAddress2, coordinatorPhone, coordinatorFax,
                               coordinatorStatus, coordinatorIncludeInProviderList, coordinatorReceivesWaiverEmails, coordinatorReceiveAppointmentText,
                               coordinatorCellPhone, coordinatorReceiveErrorText , coordinatorReceiveErrorEmails , coordinatorAdmin , coordinatorCoordinatorId ))
        db.commit()



        cursor.close(); db.close();

        return jsonify(success=True,
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500

# curl -H "Content-Type: application/json" -X DELETE -d '{"coordinatorId": "43" }'  http://127.0.0.1:8001/deleteCoordinator

@userapi.route('/deleteCoordinator/<int:coordinatorId>', methods=['DELETE'])
def deleteCoordinator(coordinatorId):
    req = request.get_json()

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.deleteCoordinator
        cursor.execute(query, (coordinatorId,))
        db.commit()

        cursor.close()
        db.close()

        return jsonify(success=True,
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500


#curl -H "Content-Type: application/json" -X POST -d '{"doctorId":"16"}'  http://127.0.0.1:8001/getDoctor

@userapi.route('/getDoctor', methods=['POST'])
def getDoctor():
    req = request.get_json()
    doctorId = req["doctorId"]

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.getDoctorById
        cursor.execute(query,(doctorId,))
        query_results = cursor.fetchall()
        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True,  data=results_dict[0],
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500




#curl -H "Content-Type: application/json" -X GET   http://127.0.0.1:8001/getDoctors

@userapi.route('/getDoctors', methods=['GET'])
def getDoctors():
    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.getDoctors
        cursor.execute(query)
        query_results = cursor.fetchall()
        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True,  data=results_dict,
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500


@userapi.route('/setDoctorOnCallById', methods=['POST'])
def setDoctorOnCallById():
    req = request.get_json()
    doctorId = req["doctorId"]
    doctorCurrent = req["onCall"]

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        if( req['onCall']):
            query = queries.unsetAllDoctorOnCall
            cursor.execute(query)
            db.commit()

        query = queries.setDoctorOnCallById
        cursor.execute(query, ( doctorCurrent , doctorId ))
        db.commit()

        query = queries.getDoctorById
        cursor.execute(query,(doctorId,))
        query_results = cursor.fetchall()

        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True, data =results_dict[0],
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500

@userapi.route('/setDoctorReceiveTextById', methods=['POST'])
def setDoctorReceiveTextById():
    req = request.get_json()
    doctorId = req["doctorId"]
    doctorReceiveText = req["receiveText"]

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500


        query = queries.setDoctorReceiveTextById
        cursor.execute(query, ( doctorReceiveText , doctorId ))
        db.commit()

        query = queries.getDoctorById
        cursor.execute(query,(doctorId,))
        query_results = cursor.fetchall()

        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True, data =results_dict[0],
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500

@userapi.route('/setDoctorReceiveEmailById', methods=['POST'])
def setDoctorReceiveEmailById():
    req = request.get_json()
    doctorId = req["doctorId"]
    doctorReceiveEmail = req["receiveEmail"]

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500


        query = queries.setDoctorReceiveEmailById
        cursor.execute(query, ( doctorReceiveEmail , doctorId ))
        db.commit()

        query = queries.getDoctorById
        cursor.execute(query,(doctorId,))
        query_results = cursor.fetchall()

        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True, data =results_dict[0],
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500


#curl -H "Content-Type: application/json" -X POST -d '{"name":"doctor one 123" , "email":"email@gmail.com" , "cellPhone":"2342342345","onCall":'1'}'  http://127.0.0.1:8001/addDoctor


@userapi.route('/addDoctor', methods=['POST'])
def addDoctor():
    req = request.get_json()
    doctorName = req["name"]
    doctorEmail = req["email"]
    doctorCellPhone = req["cellPhone"]
    doctorOnCall = req["onCall"]
    doctorReceiveEmail = req["receiveEmail"]
    doctorReceiveText = req["receiveText"]

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        if doctorOnCall == 1:
            query = queries.unsetAllDoctorOnCall
            cursor.execute(query)
            db.commit()


        query = queries.insertDoctor
        cursor.execute(query, (doctorName,doctorEmail,doctorCellPhone,doctorOnCall,doctorReceiveEmail,doctorReceiveText))
        db.commit()

        query = queries.getDoctorByEmailNameCellPhone
        cursor.execute(query,(doctorEmail,doctorName,doctorCellPhone))
        query_results = cursor.fetchall()

        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True, data =results_dict[0],
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500



#curl -H "Content-Type: application/json" -X POST -d '{"doctorId":16 , "name":"doctor one 123" , "email":"email@gmail.com" , "cellPhone":"2342342345","onCall":'1'}'  http://127.0.0.1:8001/updateDoctor


@userapi.route('/updateDoctor', methods=['POST'])
def updateDoctor():
    req = request.get_json()
    doctorName = req["name"]
    doctorEmail = req["email"]
    doctorCellPhone = req["cellPhone"]
    doctorOscarProviderNo = req["oscarProviderNo"]
    doctorOnCall = req["onCall"]
    doctorReceiveEmail = req["receiveEmail"]
    doctorReceiveText = req["receiveText"]
    doctorId = req["doctorId"]

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        if doctorOnCall == 1:
            query = queries.unsetAllDoctorOnCall
            cursor.execute(query)
            db.commit()


        query = queries.updateDoctor
        cursor.execute(query, (doctorName,doctorEmail,doctorCellPhone,doctorOscarProviderNo,doctorOnCall,doctorReceiveEmail,doctorReceiveText,doctorId))
        db.commit()



        cursor.close(); db.close();

        return jsonify(success=True,
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500



#curl -H "Content-Type: application/json" -X DELETE -d '{"doctorId": "43" }'  http://127.0.0.1:8001/deleteDoctor


@userapi.route('/deleteDoctor/<int:doctorId>', methods=['DELETE'])
def deleteDoctor(doctorId):
    req = request.get_json()

    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.deleteDoctor
        cursor.execute(query, (doctorId,))
        db.commit()

        cursor.close(); db.close();

        return jsonify(success=True,
                       error={'code': 200, 'message': "OK"})

    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500

#curl -H "Content-Type: application/json" -X POST -d '{"data":[{"cellPhone": "123","current": 0,"email": "arzuatilgan@yahoo.com","name": "a" },{"cellPhone": "1231231234","current": 0,"email": "dbrooks60@rogers.com","name": "Dr. Doolittle" }]}'  http://127.0.0.1:8001/setDoctors

@userapi.route('/setDoctors', methods=['POST'])
def setDoctors():
    req = request.get_json()
    doctorList = req["data"]


    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        query = queries.archiveAllDoctors
        cursor.execute(query)
        db.commit()

        for doctor in doctorList:
                query = queries.insertDoctor
                cursor.execute(query, (doctor['email'],doctor['name'],doctor['cellPhone'],doctor['current']))
                db.commit()

        query = queries.removeArchivedDoctors
        cursor.execute(query)
        db.commit()


        query = queries.getDoctors
        cursor.execute(query)
        query_results = cursor.fetchall()
        cursor.close(); db.close();

        results_dict = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]
        return jsonify(success=True,  data=results_dict,
                       error={'code': 200, 'message': "OK"})


    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500


@userapi.route('/updateAppointmentStatus', methods=['POST'])
def updateAppointmentStatus():
    req = request.get_json()
    status = req["status"]
    caseId = req["caseId"]
    demographicNo = req['demographicNo']



    if not app.config['DEBUG'] and 'authid' not in session:
        return jsonify(ae.NotLoggedIn().errDict()), ae.NotLoggedIn().code
    try:

        (db, cursor, message) = DB.connect()
        if db == None:
            return jsonify(success=False,
                           error={'code': 500, 'message': message}), 500

        case_obj = oscar.get_case_info(caseId )
        case_obj['status'] = status

        log.info( "new case_obj = " + str(case_obj) )

        try:
            oscar.update_case_info(case_obj)
        except Exception as e:
            cursor.close(); db.close();
            return jsonify(ae.DatabaseError().errDict()), ae.DatabaseError().code


        query = queries.updateAppointmentStatus
        cursor.execute(query, (status,caseId))
        db.commit()


        query = queries.getCurrentAppointments
        cursor.execute(query, ( demographicNo,) );
        query_results = cursor.fetchall()


        results_dict_current = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        query = queries.getPastAppointments
        cursor.execute(query, ( demographicNo,) );
        query_results = cursor.fetchall()

        cursor.close(); db.close();

        results_dict_past = [dict(zip([c[0] for c in cursor.description], qr)) for qr in query_results]

        return jsonify(success=True,
                       error={'code': 200, 'message': "OK"},
                       data={'currentAppointments':results_dict_current , 'pastAppointments':results_dict_past } )


    except Exception as e:
        log.exception(str(e))
        return jsonify(success=False,
                       error={'code': 500, 'message': str(e)}), 500


@userapi.route('/errortest', methods=['GET'])
def errortest():
    try:
        badbad = 1 / 0;
    except Exception as e:
        log.exception(str(e))
    return jsonify(success=True,
                       error={'code': 500, 'message': 'error has been thrown. check your email'}), 500




app.register_blueprint( userapi )





