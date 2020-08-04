from twilio.rest import Client
import speech_recognition as sr
import requests
from bs4 import BeautifulSoup, Tag
import os
from os import path



# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure

if(path.exists("audios")!=True):
    os.mkdir("audios")

if(path.exists("transcriptions")!=True):
    os.mkdir("transcriptions")

account_sid = '__'
auth_token = '__'


response =requests.get("https://api.twilio.com/2010-04-01/Accounts/__/Recordings",auth=(account_sid, auth_token))       #v1/Recordings        #client.video.v1.Recordings
xmls = BeautifulSoup(response.content,features="lxml")

rid_list = []


for tags in xmls.find_all("sid"):
    rid_list.append(tags.string)

for rids in rid_list:
    response = requests.get("https://api.twilio.com/2010-04-01/Accounts/{0}/Recordings/{1}".format(account_sid,rids))
    fileName= "audios/"+rids+".wav"
    try:
        with open(fileName, mode='bx') as f:
            f.write(response.content)
    except:
        print(rids+".wav already created")
        pass



for rids in rid_list:
    sound = "audios/"+rids+".wav"
    r=sr.Recognizer()

    with sr.AudioFile(sound) as source:
        r.adjust_for_ambient_noise(source)
        print("Converting "+sound+" to text...")
        audio=r.listen(source)

        fileName="transcriptions/"+rids+".txt"
        if(path.exists(fileName)):
            print(fileName+" already downloaded. Trying next. \n")
            continue
        else:
            a=open(fileName,"x")
            print("Converted Audio to "+fileName)
            a.write(r.recognize_google(audio)+"\n")
            a.close()


print("All calls downloaded and transcribed")    


