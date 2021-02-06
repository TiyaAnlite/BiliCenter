import time
import json
import random

import requests


def main_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Received context: " + str(context))
    time.sleep(random.randint(1, 8) / 10)
    ip = requests.get("https://api.focot.cn/public/ip").json()
    return ip
