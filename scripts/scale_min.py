import RPi.GPIO as GPIO
import time

# Pins
DOUT_PIN = 17
SCK_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(SCK_PIN, GPIO.OUT)
GPIO.setup(DOUT_PIN, GPIO.IN)

def read_hx711():
    # Wait for DOUT to go low (data ready)
    while GPIO.input(DOUT_PIN) == 1:
        time.sleep(0.001)
    
    count = 0
    for _ in range(24):
        GPIO.output(SCK_PIN, True)
        count = (count << 1) | GPIO.input(DOUT_PIN)
        GPIO.output(SCK_PIN, False)
    
    # Pulse SCK one more time to set gain/channel
    GPIO.output(SCK_PIN, True)
    GPIO.output(SCK_PIN, False)

    # Convert from 24-bit two's complement
    if count & 0x800000:
        count |= ~0xffffff  # sign extend
    return count

try:
    while True:
        value = read_hx711()
        print("Raw HX711 value:", value)
        time.sleep(0.5)
finally:
    GPIO.cleanup()
