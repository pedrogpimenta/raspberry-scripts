#!/usr/bin/python
import os
from os.path import join, dirname
from dotenv import load_dotenv
import time
import json
import requests

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
mailgun_api = os.getenv('MAILGUN_API')

def airsonic_up():
    try:
        response = requests.get("http://127.0.0.1:4080/api/tunnels")
        data = response.json()
        ngrok_url = data["tunnels"][0]["public_url"]
        return ngrok_url
    except:
        return False

def send_simple_message(message):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org/messages",
        auth=("api", mailgun_api),
        data={"from": "Raspberry Home <mailgun@sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org>",
            "to": ["pedro@pimenta.co"],
            "subject": "I'm up",
            "text": message})

time.sleep(60)
ngrok_url_out = airsonic_up()

if ngrok_url_out:
    send_simple_message("Ngrok address is: " + ngrok_url_out)
