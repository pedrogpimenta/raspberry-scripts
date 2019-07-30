#!/usr/bin/python2.7
import os
from os.path import join, dirname
from dotenv import load_dotenv
import json
import requests
import re
from datetime import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
mailgun_api = os.getenv('MAILGUN_API')
cloudflare_api = os.getenv('CLOUDFLARE_API')

home_file = join(dirname(__file__), 'current_home')
music_file = join(dirname(__file__), 'current_music')
ssh_file = join(dirname(__file__), 'current_ssh')
vnc_file = join(dirname(__file__), 'current_vnc')

read_home_url = open(home_file, 'r')
current_home_url = read_home_url.read()
read_music_url = open(music_file, 'r')
current_music_url = read_music_url.read()
read_ssh_url = open(ssh_file, 'r')
current_ssh_url = read_ssh_url.read()
read_vnc_url = open(vnc_file, 'r')
current_vnc_url = read_vnc_url.read()

home_url = music_url = ssh_url = vnc_url = 'unavailable'

def update_html():
    with open('/var/www/home/index.html', 'r') as file:
        global music_url
        global ssh_url
        global vnc_url

        data = 'Music: ' + music_url + '\n<br />SSH: ' + ssh_url + '\n<br />VNC: ' + vnc_url + '\n<br />Updated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'

        with open('/var/www/home/index.html', 'w') as file:
            file.writelines( data )

def set_urls():
    global home_url
    global music_url
    global ssh_url
    global vnc_url
    try:
        response = requests.get("http://127.0.0.1:4080/api/tunnels")
        data = response.json()
        tunnels = data["tunnels"]
        for tunnel in tunnels:
            if tunnel["name"] == "home":
                home_url = tunnel["public_url"]
            if tunnel["name"] == "music":
                music_url = tunnel["public_url"]
            if tunnel["name"] == "ssh":
                ssh_url = tunnel["public_url"]
            if tunnel["name"] == "vnc":
                vnc_url = tunnel["public_url"]
        print 'All good.'
    except:
        print 'Ngrok is not running.'
        return False

def set_redir(url, target, pagerule):
    try:
        cf_url = "https://api.cloudflare.com/client/v4/zones/b6244deaa244bc53a3d3ce9cc9fe0d29/pagerules/" + pagerule
        headers = {"X-Auth-Email": "pedro@pimenta.co", "X-Auth-Key": cloudflare_api, "Content-Type": "application/json"}
        data = {
            "targets": [
                {
                    "target": "url",
                    "constraint": {
                        "operator": "matches",
                        "value": target + ".pimenta.co/*"
                    }
                }
            ],
            "actions": [
                {
                    "id": "forwarding_url",
                    "value": {
                        "url": url,
                        "status_code": 301
                    }
                }
            ],
            "priority": 1,
            "status": "active"
        }
        patch = requests.patch(cf_url, headers=headers, json=data)
        print "Cloudflare redirection has been set."
    except:
        return False

def send_simple_message(subject, message):
    print "Email has been sent."
    return requests.post(
        "https://api.mailgun.net/v3/sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org/messages",
        auth=("api", mailgun_api),
        data={"from": "Raspberry Home <mailgun@sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org>",
            "to": ["pedro@pimenta.co"],
            "subject": subject,
            "text": message})

set_urls()

print 'Home URL: ' + home_url
print 'Music URL: ' + music_url
print 'SSH URL: ' + ssh_url
print 'VNC URL: ' + vnc_url

if (home_url != current_home_url) or (music_url != current_music_url) or (ssh_url != current_ssh_url) or (vnc_url != current_vnc_url):
    write_home = open(home_file, 'w')
    write_home.write(home_url)
    write_home.close()
    write_music = open(music_file, 'w')
    write_music.write(music_url)
    write_music.close()
    write_ssh = open(ssh_file, 'w')
    write_ssh.write(ssh_url)
    write_ssh.close()
    write_vnc = open(vnc_file, 'w')
    write_vnc.write(vnc_url)
    write_vnc.close()
    music_url_redir = music_url + "/$1"
    home_url_redir = home_url + "/$1"
    set_redir(music_url_redir, 'music', '232fc4b6e1e7ac1d4e9728a8485a7706')
    set_redir(home_url_redir, 'home', '614e7c325b2a0b890a87f34f47d53fe2')
    send_simple_message("New Ngrok addresses", "Home address is: " + home_url + ".\nMusic address is: " + music_url + ".\nSSH address is: " + ssh_url + ".\nVNC address is: " + vnc_url + ".")

update_html()
