#!/usr/bin/env python3

from flask import Flask, redirect, request
from log import log
from config import HOSTLISTEN, DEBUG

app = Flask(__name__)

def force_ssl():
    url = request.url.replace('http://', 'https://', 1)
    return redirect(url, code=301)

app.before_request(force_ssl)


if __name__ == '__main__':
    app.run( debug=DEBUG, port=80, host=HOSTLISTEN)


