#!/usr/bin/python
import os
from os.path import join, dirname
from dotenv import load_dotenv
import time
import json
import requests

dotenv_path = '/home/pi/Scripts/.env'
load_dotenv(dotenv_path)
mailgun_api = os.getenv('MAILGUN_API')
cloudflare_api = os.getenv('CLOUDFLARE_API')

def airsonic_up():
    try:
        response = requests.get("http://127.0.0.1:4080/api/tunnels")
        data = response.json()
        tunnels = data["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                ngrok_url = tunnel["public_url"]
        return ngrok_url
    except:
        return False

def set_redir(ngrok_url):
    try:
        url = "https://api.cloudflare.com/client/v4/zones/b6244deaa244bc53a3d3ce9cc9fe0d29/pagerules/db81da25b729d71348c0eb1962228a0b"
        headers = {"X-Auth-Email": "pedro@pimenta.co", "X-Auth-Key": cloudflare_api, "Content-Type": "application/json"}
        data = {
            "targets": [
                {
                    "target": "url",
                    "constraint": {
                        "operator": "matches",
                        "value": "music.pimenta.co/"
                    }
                }
            ],
            "actions": [
                {
                    "id": "forwarding_url",
                    "value": {
                        "url": ngrok_url,
                        "status_code": 301
                    }
                }
            ],
            "priority": 1,
            "status": "active"
        }
        patch = requests.patch(url, headers=headers, json=data)
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

ngrok_url_out = airsonic_up()

send_simple_message("Pi just booted up")

if ngrok_url_out != False:
    url_for_dns = ngrok_url_out + "/airsonic/"
    set_redir(url_for_dns)
    send_simple_message("Ngrok address is: " + ngrok_url_out)
else:
    send_simple_message("Ngrok not found")

