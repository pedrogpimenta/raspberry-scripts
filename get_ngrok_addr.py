#!/usr/bin/python2.7
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
            if tunnel["proto"] == "http":
                ngrok_url = tunnel["public_url"]
        return ngrok_url
    except:
        return False

def ngrok_ssh_url():
    try:
        response = requests.get("http://127.0.0.1:4080/api/tunnels")
        data = response.json()
        tunnels = data["tunnels"]
        for tunnel in tunnels:
            if tunnel["name"] == "ssh":
                ssh_url = tunnel["public_url"]
        return ssh_url
    except:
        return False

def ngrok_vnc_url():
    try:
        response = requests.get("http://127.0.0.1:4080/api/tunnels")
        data = response.json()
        tunnels = data["tunnels"]
        for tunnel in tunnels:
            if tunnel["name"] == "vnc":
                ssh_url = tunnel["public_url"]
        return ssh_url
    except:
        return False

def set_redir(ngrok_url):
    try:
        url = "https://api.cloudflare.com/client/v4/zones/b6244deaa244bc53a3d3ce9cc9fe0d29/pagerules/232fc4b6e1e7ac1d4e9728a8485a7706"
        headers = {"X-Auth-Email": "pedro@pimenta.co", "X-Auth-Key": cloudflare_api, "Content-Type": "application/json"}
        data = {
            "targets": [
                {
                    "target": "url",
                    "constraint": {
                        "operator": "matches",
                        "value": "music.pimenta.co/*"
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

time.sleep(60)

def send_simple_message(subject, message):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org/messages",
        auth=("api", mailgun_api),
        data={"from": "Raspberry Home <mailgun@sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org>",
            "to": ["pedro@pimenta.co"],
            "subject": subject,
            "text": message})

ngrok_url_out = airsonic_up()
ssh_url = ngrok_ssh_url()
vnc_url = ngrok_vnc_url()

send_simple_message("I'm up", "Pi just booted up")

if ngrok_url_out != False:
    url_for_dns = ngrok_url_out + "/$1"
    set_redir(url_for_dns)
    send_simple_message("New Ngrok address", "Ngrok address is: " + ngrok_url_out + ".\nSSH address is: " + ssh_url + ".\nVNC address is: " + vnc_url + ".")
else:
    send_simple_message("Ngrok error", "Ngrok not found")























