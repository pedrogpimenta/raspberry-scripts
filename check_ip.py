#!/usr/bin/python2.7
import os
from os.path import join, dirname
from dotenv import load_dotenv
import time
import requests
from requests import get

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
mailgun_api = os.getenv('MAILGUN_API')

def send_simple_message(message):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org/messages",
        auth=("api", mailgun_api),
        data={"from": "Raspberry Home <mailgun@sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org>",
            "to": ["pedro@pimenta.co"],
            "subject": "I have a new IP",
            "text": message})

time.sleep(60)

extip = requests.get('https://api.ipify.org').text

ip_file = join(dirname(__file__), 'current_ip')
readFile = open(ip_file, "r") 
fileipcontent = readFile.read()
readFile.close()

if (fileipcontent == extip):
    exit()
else:
    writeFile = open(ip_file, "w")
    writeFile.write(extip)
    writeFile.close()
    send_simple_message("The new IP address is: " + extip)
