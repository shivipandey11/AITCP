from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import pandas as pd

application = Flask(__name__)

#Call Server cd to current directory, then> ngrok.exe http 5000

@application.route("/")
def hello():
    return "Hello World!" #To test working of server

@application.route("/record", methods=['GET', 'POST'])
def record():
    #Add check for spam caller here, sample code follows
    response = VoiceResponse()
    block_call = False
    phoneNumber = request.form.get('From')
    # response.say(phoneNumber)
    data = pd.read_csv('Blacklist.csv', dtype=object)
    phoneNumbers=data.Numbers.tolist()
    print(phoneNumbers)
    if phoneNumber[1:] in phoneNumbers:
                block_call = True
    if block_call:
        response.say('Hello. This Number is BlackListed.')
        response.reject()
    response.say('Hello. Please leave a message after the beep.')

    response.record()

    response.hangup()

    return str(response)





if __name__ == "__main__":
    application.run(debug=True)
