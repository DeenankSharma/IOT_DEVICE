import RPi.GPIO as GPIO
import time
import requests

URL = ""

def send_lab_updates():
    r = requests.get(url=URL)
    return r.json()

led_pin = 22
button_pin = 4
lab_open = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin,GPIO.OUT)
GPIO.setup(button_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.output(led_pin,GPIO.LOW)

# previous_state = GPIO.input(button_pin)
lab_msg_sent = False

while True:
    button_state = GPIO.input(button_pin)
    if button_state == GPIO.HIGH and lab_msg_sent == False:
        data = send_lab_updates()
        print("pehle wala called")
#         data = data_.json()
        time.sleep(5)
        if data["slackResponse"]["message"]["text"] == "Bro lab is open":
            GPIO.output(led_pin,GPIO.HIGH)
            lab_msg_sent = True
#         print("led is on")
    elif lab_msg_sent == True and button_state == GPIO.LOW:
        data = send_lab_updates()
        print("doosre wala called")
#         data = data_.json()
        time.sleep(5)
        if data["slackResponse"]["message"]["text"] == "Bro lab is closed":
            GPIO.output(led_pin,GPIO.LOW)
            lab_msg_sent = False
#         GPIO.output(led_pin,GPIO.LOW)
#         print("led is off")
    time.sleep(0.1)
    
    
GPIO.cleanup()

