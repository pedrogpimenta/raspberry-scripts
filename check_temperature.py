import os
from os.path import join, dirname
from dotenv import load_dotenv
import psutil
import subprocess
import requests
from gpiozero import CPUTemperature

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
mailgun_api = os.getenv('MAILGUN_API')

def send_simple_message(message):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org/messages",
        auth=("api", mailgun_api),
        data={"from": "Raspberry Home <mailgun@sandbox8a35a11f1c414544ad1e456e24756f9b.mailgun.org>",
            "to": ["pedro@pimenta.co"],
            "subject": "I'm too hot!",
            "text": message})

cpu = int(CPUTemperature().temperature)
gpu = os.popen('vcgencmd measure_temp | egrep -o \'[0-9]*\.[0-9]*\'').readline()
gputemp = float(gpu)

if (gputemp > 65):
    send_simple_message("The GPU is too hot at " + str(gputemp) + " degrees celcius.")

if (cpu > 65):
    send_simple_message("The GPU is too hot at " + str(cpu) + " degrees celcius.")

