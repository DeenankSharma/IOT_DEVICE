import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17
BUZZER_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN,GPIO.OUT)

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            GPIO.output(BUZZER_PIN,GPIO.HIGH)
        else:
            GPIO.output(BUZZER_PIN,GPIO.LOW)
        time.sleep(0.05)

except KeyboardInterrupt:
    print('exiting program')

finally:
    GPIO.cleanup()