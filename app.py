#!/usr/bin/env python3

import os
import logging
import oscar
from flask import Flask, render_template, session, Blueprint, redirect, request,jsonify
from log import log
from config import app
import config
import ssl
from flask_mail import Mail

from userapi import userapi, randomString, setAppointmentRequestToken
import platform

app.register_blueprint( userapi )


@app.route('/splash')
@app.route('/register')
@app.route('/help')
def notLoggedInEndpoint():
    return render_template(request.full_path.replace( "/" , "").replace("?","") + '.html')

@app.route('/newAppointment')
@app.route('/authorization')
@app.route('/manageCoordinators')
@app.route('/dashboard')
@app.route('/oncallDoctors')
def loggedInEndpoint():
    if 'authid' not in session or '_cmd-email_' not in request.cookies:
        return redirect('/login', 302)
    return render_template(request.full_path.replace( "/" , "").replace("?","") + '.html')


@app.route('/login')
def login():
    # No point in sending them to login page if they already are
    if 'authid' in session and '_cmd-email_' in request.cookies:
       return redirect('/dashboard', 302)
    return render_template('login.html')


@app.route('/activate/<coordinator_id>/<email_activation_token>')
def activateGet(coordinator_id, email_activation_token):
    # signOut()
    return render_template('set_password.html')

@app.route('/resetpassword/<coordinator_id>/<email_activation_token>')
def resetPasswordGet(coordinator_id , email_activation_token):
    return render_template('reset_password.html')



@app.route('/signOut')
def signOut():
    session.clear()
    res = redirect('/login', 302)
    res.set_cookie("_cmd-email_", expires=0)
    return res


@app.route('/getLoggedOutContent', methods=['POST'])
def getLoggedOutContent():
    req = request.get_json()

    if app.config['DONT_LOG_OUT'] == False:
        session.clear()
    if platform.system() == 'Windows':
        f = open('static\\'+req["content"], 'r' ,encoding="utf8")
    else:
        f = open('static/'+req["content"], 'r')
    content = f.read()
    res = jsonify( success = True, data=content,
                        error = {'code': 200, 'message': "OK" })
    session["appointmentRequest"] = randomString(20)
    session.modified = True

    setAppointmentRequestToken( session["appointmentRequest"] )

    if app.config['DONT_LOG_OUT'] == False:
        res.set_cookie("_cmd-email_", expires=0)
    res.set_cookie("_cmd-demographic_", value=str(req["demographicNo"]) , expires=3600)

    return res

@app.route('/')
def index():
    return render_template( 'splash.html')



if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('keys/clickmd.crt', keyfile='keys/clickmd.key')
    context.options |= ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1 | ssl.OP_NO_SSLv3 | ssl.OP_NO_SSLv2
    context.set_ciphers('ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:RSA+AESGCM:RSA+AES:!aNULL:!MD5:!DSS')
    app.secret_key = b'GN\xe0\xe60y?s\x94\xdc\xbd6\x07\xe2\xc0\x99\xceE\xa6#l7\x9f\xca'
    app.run( debug=app.config['DEBUG'], ssl_context=None if app.config['DEBUG'] else context, port=app.config['PORTLISTEN'] , host=app.config['HOSTLISTEN'])


