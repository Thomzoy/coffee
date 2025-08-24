import RPi.GPIO as GPIO
import time

INT_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(INT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def cb(channel):
    print("Edge detected!")

GPIO.add_event_detect(INT_PIN, GPIO.FALLING, callback=cb, bouncetime=200)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
