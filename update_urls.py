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

ampache_file = join(dirname(__file__), 'current_ampache')
ssh_file = join(dirname(__file__), 'current_ssh')
vnc_file = join(dirname(__file__), 'current_vnc')

read_ampache_url = open(ampache_file, 'r')
current_ampache_url = read_ampache_url.read()
read_ssh_url = open(ssh_file, 'r')
current_ssh_url = read_ssh_url.read()
read_vnc_url = open(vnc_file, 'r')
current_vnc_url = read_vnc_url.read()

ampache_url = ssh_url = vnc_url = 'unavailable'

#def update_html():
#    with open('/var/lib/tomcat8/webapps/ROOT/index.html', 'r') as file:
#        global ampache_url
#        global ssh_url
#        global vnc_url
#
#        data = file.readlines()
#
#        linenumber = 0
#        for line in data:
#            if re.search(r'ampache-url', line):
#                data[linenumber+1] = ampache_url + '\n'
#            if re.search(r'ssh-url', line):
#                data[linenumber+1] = ssh_url + '\n'
#            if re.search(r'vnc-url', line):
#                data[linenumber+1] = vnc_url + '\n'
#            if re.search(r'last-update-date', line):
#                data[linenumber+1] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'
#            linenumber += 1
#
#        with open('/var/lib/tomcat8/webapps/ROOT/index.html', 'w') as file:
#            file.writelines( data )

def set_urls():
    global ampache_url
    global ssh_url
    global vnc_url
    try:
        response = requests.get("http://127.0.0.1:4080/api/tunnels")
        data = response.json()
        tunnels = data["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "http":
                ampache_url = tunnel["public_url"]
            if tunnel["name"] == "ssh":
                ssh_url = tunnel["public_url"]
            if tunnel["name"] == "vnc":
                vnc_url = tunnel["public_url"]
        print 'All good.'
    except:
        print 'Ngrok is not running.'
        return False

def set_redir(url):
    try:
        cf_url = "https://api.cloudflare.com/client/v4/zones/b6244deaa244bc53a3d3ce9cc9fe0d29/pagerules/232fc4b6e1e7ac1d4e9728a8485a7706"
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

print 'Ampache URL: ' + ampache_url
print 'SSH URL: ' + ssh_url
print 'VNC URL: ' + vnc_url

if (ampache_url != current_ampache_url) or (ssh_url != current_ssh_url) or (vnc_url != current_vnc_url):
    write_ampache = open(ampache_file, 'w')
    write_ampache.write(ampache_url)
    write_ampache.close()
    write_ssh = open(ssh_file, 'w')
    write_ssh.write(ssh_url)
    write_ssh.close()
    write_vnc = open(vnc_file, 'w')
    write_vnc.write(vnc_url)
    write_vnc.close()
    url_for_dns = ampache_url + "/$1"
    set_redir(url_for_dns)
    #update_html()
    send_simple_message("New Ngrok addresses", "Ampache address is: " + ampache_url + ".\nSSH address is: " + ssh_url + ".\nVNC address is: " + vnc_url + ".")
