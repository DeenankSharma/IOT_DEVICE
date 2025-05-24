import RPi.GPIO as GPIO
import time

led_pin = 22
button_pin = 4
lab_open = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin,GPIO.OUT)
GPIO.setup(button_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.output(led_pin,GPIO.LOW)

# previous_state = GPIO.input(button_pin)

while True:
    button_state = GPIO.input(button_pin)
    if button_state == GPIO.HIGH:
        GPIO.output(led_pin,GPIO.HIGH)
        print("led is on")
    else:
        GPIO.output(led_pin,GPIO.LOW)
        print("led is off")
    time.sleep(0.1)
    
    
GPIO.cleanup()
