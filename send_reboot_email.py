import os
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime
import requests

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
mailgun_api = os.getenv('MAILGUN_API')

def send_simple_message(message):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org/messages",
        auth=("api", mailgun_api),
        data={"from": "Raspberry Home <mailgun@sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org>",
            "to": ["pedro@pimenta.co"],
            "subject": "I just woke up!",
            "text": message})

last_time_updated = os.path.getmtime('/home/pi/Scripts/update_urls.log')
last_time_updated_good = datetime.utcfromtimestamp(last_time_updated).strftime('%Y-%m-%d %H:%M:%S')

send_simple_message('Something happened, but now I\'m up! Last time URLs were updated was: ' + last_time_updated_good)
