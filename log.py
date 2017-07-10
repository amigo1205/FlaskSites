#!flask/bin/python
import os, sys, re, json
import platform
from config import app
import logging
import datetime
from logging.handlers import RotatingFileHandler
import random
import shlex, subprocess
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import database as DB
import queries


import traceback

mainAlgoDir = os.path.dirname(os.path.abspath(__file__))
LOGFILENAME = mainAlgoDir + "/log/logfile.txt"


regexString = """cpu:\/docker\/(.+)"""
regexString2 = """docker-(.+)\.scope"""

try:
    if platform.system() == 'Windows':
        searchResults = None;
    else:
        procFile = open('/proc/self/cgroup').read()
        # Try early version container scrape; if nothing comes back, try the later version
        searchResults = re.search(regexString,procFile)
        if searchResults is None:
            searchResults = re.search(regexString2,procFile)

except Exception as e:
    searchResults = None;


mainAlgoName = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
  with open(mainAlgoDir + "/.git/config") as configFile:
    config = configFile.read()
    mainAlgoNameCandidate = re.search('origin"].*\/(.*?)\.git',config.replace("\n","")).group(1)
    if mainAlgoName is not None and len(mainAlgoName) > 0: mainAlgoName = mainAlgoNameCandidate
except: pass #if there's a problem with getting the name from git, screw it, use the directory name

if searchResults is None:
    dockerID = 'LOCAL'
    containerString = "(" + mainAlgoName + ")"
    dockerControlString = "NotDocker." + ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
else:
    dockerID = searchResults.group(1)[:12]
    containerString = "(" + mainAlgoName + ":" + dockerID[0:3] + ")"
    dockerControlString = searchResults.group(1)[0:3]

def shellCmd(cmd): return subprocess.check_output(shlex.split(cmd)).decode('utf8')

try:
    recordGitDataScript = os.path.dirname(__file__) + '/recordGitData.sh'
    gitData = json.loads(shellCmd("bash %s" % recordGitDataScript))
    latestCommitString = "{commit} {message}\n{timestamp}".format(**gitData)

except Exception as e:
    latestCommitString = "commit string could not be parsed, not valid json"

#latestCommitString = check_output(shlex.split("git log -1 --date=short --pretty=\"%h %B %cd\"")).decode("utf8").replace("\n","")

# This custom logger will add the jobID.
class JobIDLogger(logging.LoggerAdapter):
    jobID = "="
    def setJobID(self,newID):
        self.jobID = newID

    def exception(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        self.logger.exception(msg, *args, **kwargs)
        #emails = os.getenv("EXCEPTION_EMAIL", "").split(',')
        #emails is list of email addresses
        (db, cursor, message) = DB.connect(logErrors=False)
        if db == None:
            return

        query = queries.getEmailsForErrorMessage
        cursor.execute(query )
        query_results = cursor.fetchall()
        emails = []
        for e in query_results:
            emails.append( e[0] )


#        if not app.config['DEBUG'] and len(emails[0]) > 0:
        if len(emails[0]) > 0:

            stackTraceString = traceback.format_exc(20)
            stackTraceString = stackTraceString.replace("\n" , "<br>" )

            # Send email to admins about this exception
            server = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"])
            server.starttls()
            server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            content = MIMEMultipart()
            content['Subject'] = "Exception thrown at ClickMD"
            content['From'] = app.config["MAIL_USERNAME"]
            content['To'] = emails[0]
            if len(emails) > 1:
                content['cc'] = ", ".join(emails[1:])
            body = MIMEText("<p>The following exception was logged at " + str(datetime.datetime.now()) + ":</p><br/>" + stackTraceString)
            body.replace_header("Content-Type", "text/html")
            content.attach(body)
            server.sendmail(app.config["MAIL_USERNAME"], emails, content.as_string())
            server.quit()

    def process(self, msg, kwargs):
        return "<%s> %s" % (self.jobID,msg), kwargs

if not os.path.isdir(os.path.dirname(LOGFILENAME)):
    os.mkdir(os.path.dirname(LOGFILENAME))
if not os.path.isfile(LOGFILENAME):
    open(LOGFILENAME, 'a').close()

# Create Log formatter, base job object
formatter = logging.Formatter("%(asctime)s "+containerString+" [%(filename)s:%(lineno)d] %(levelname)s %(message)s")
syslogfmt = logging.Formatter(containerString+" [%(filename)s:%(lineno)d] %(levelname)s %(message)s")
logBase = logging.getLogger(__name__)
logBase.setLevel(logging.DEBUG)

# Log to console (Just for debugging convenience)
stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setLevel(logging.DEBUG)
stdoutHandler.setFormatter(formatter)
logBase.addHandler(stdoutHandler)

# Log locally to a file
rotateFileHandler = RotatingFileHandler(LOGFILENAME, maxBytes=10000000, backupCount=5)
rotateFileHandler.setLevel(logging.INFO)
rotateFileHandler.setFormatter(formatter)
logBase.addHandler(rotateFileHandler)

# Logs to local Syslog, which will be mirrored from there to the central log server

if platform.system() != 'Windows':
    localSyslogHandler = logging.handlers.SysLogHandler(address=("/dev/log"), facility=16)
    localSyslogHandler.setLevel(logging.INFO)
    localSyslogHandler.setFormatter(syslogfmt)
    logBase.addHandler(localSyslogHandler)

log = JobIDLogger(logBase, {'jobID': "Not Used"})

log.info("Using Software Version: %s" % format (latestCommitString))

