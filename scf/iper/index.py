import requests
import json


def main_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Received context: " + str(context))
    ip = requests.get("https://api.focot.cn/public/ip").json()
    return ip
