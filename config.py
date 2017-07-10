import os
from flask import Flask, render_template_string


app = Flask(__name__, static_url_path='/static')

HOSTLISTEN = '127.0.0.1'
PORTLISTEN = int(os.getenv('PORT', "4000" ))
DEBUG = (True if os.getenv('DEBUG', 'False' ).upper() == 'TRUE' else False)
DONT_LOG_OUT = (True if os.getenv('DONT_LOG_OUT', 'False' ).upper() == 'TRUE' else False)


# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
#    smtpOptions :
#    {
#      port      : 25,
#      host      : 'mail.dataesp.ca',
#      emailFrom : 'accounts@dataesp.ca',
#      tls: {rejectUnauthorized: false},
#      auth: {
#        user: 'accounts@dataesp.ca',
#        pass: 'config.py'
#      }
#    },

SECRET_KEY =              os.getenv('SECRET_KEY',       'dataesp is dataesp')
CSRF_ENABLED = True

# Flask-Mail settings
MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        'accounts@clickmd.ca')
MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  'ClickMD <accounts@clickmd.ca>')
MAIL_SERVER =             os.getenv('MAIL_SERVER',          'smtp.gmail.com')
MAIL_PORT =           int(os.getenv('MAIL_PORT',            '587'))
MAIL_USE_SSL =        int(os.getenv('MAIL_USE_SSL',         True))

#MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        'accounts@dataesp.ca')
#MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  'ClickMD <accounts@dataesp.ca>')
#MAIL_SERVER =             os.getenv('MAIL_SERVER',          'repo.dataesp.net')
#MAIL_PORT =           int(os.getenv('MAIL_PORT',            '465'))
#MAIL_USE_SSL =        int(os.getenv('MAIL_USE_SSL',         True))

MAIL_PASSWORD =           os.getenv('MAIL_PASSWORD',        'config.py')




# Flask-User settings
USER_APP_NAME        = os.getenv('USER_APP_NAME',          'ClickMD')                # Used by email templates


app.config.from_object( __name__ )






