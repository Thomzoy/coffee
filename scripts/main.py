#! /home/dietpi/coffee/.venv//bin/activate

import time
import signal

from coffee.app.app import LCDApp
from coffee.io.encoder import Encoder
from coffee.io.multiplex import Multiplex
from coffee.io.scale import Scale

app = LCDApp()

encoder = Encoder(
    clk_pin=26,
    data_pin=21,
    encoder_button_pin=20,
    red_button_pin=18,
)

multiplex = Multiplex(
    interrupt_pin=4,
)

scale = Scale(
    smoothing_window=7,
)

app.set_inputs(scale=scale, multiplex=multiplex, encoder=encoder)
app.display()

from threading import Event
import signal

exit = Event()

def main():
    while not exit.is_set():
      do_my_thing()
      exit.wait(60)

    print("All done!")
    # perform any cleanup here

def quit(signo, _frame):
    print("Interrupted by %d, shutting down" % signo)
    exit.set()

signal.signal(signal.SIGTERM, quit)
signal.signal(signal.SIGINT, quit)
signal.signal(signal.SIGHUP, quit)        

try:
    scale.start_reading()
    while not exit.is_set():
        multiplex.mcp.digital_read_all()
        app.check_timeout()
        #exit.wait(0.5)
        time.sleep(0.5)
except Exception as e:
    raise e
finally:
    scale.stop_reading()
    multiplex.cleanup()
    encoder.cleanup()
    #GPIO.cleanup()
