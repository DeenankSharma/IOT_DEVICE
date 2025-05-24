import requests

URL = ""

def send_lab_updates():
    r = requests.get(url=URL)
    print(r.json())
    
send_lab_updates()