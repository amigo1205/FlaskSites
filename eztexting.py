import pycurl
from io import BytesIO
from io import StringIO
from log import log

try:
    import simplejson as json
except ImportError:
    import json



def send_sms(textRecipients, textSubject , textMessage):
    try:
        curl = pycurl.Curl()
        curl.setopt(curl.SSL_VERIFYPEER, 1)
        curl.setopt(curl.SSL_VERIFYHOST, 2)
        curl.setopt(curl.CAINFO, "cacert.pem")
        curl.setopt(curl.VERBOSE, True)

        params = "User=clickmd&Password=Westside2380&Subject=" + textSubject + "&Message=" + textMessage + textRecipients + "&MessageTypeID=1"
        curl.setopt(curl.POSTFIELDS, params)

        curl.setopt(curl.URL, "https://app.eztexting.com/sending/messages?format=json")

        contents = BytesIO()
        curl.setopt(curl.WRITEDATA, contents )

        curl.perform()
        contents = contents.getvalue().decode("utf8")

        log.info( "\n=== SMS TEXT RESPONSE ========\n" + contents + "\n==============================\n"  )

        responseCode = curl.getinfo(pycurl.HTTP_CODE);
        isSuccessResponse = responseCode < 400;

        curl.close()

        if not isSuccessResponse:
            raise Exception( contents )
    except Exception as e:
        log.exception( str(e) )


