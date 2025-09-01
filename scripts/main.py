#! /home/dietpi/coffee/.venv//bin/activate

import time

from coffee.io.encoder import Encoder
from coffee.io.multiplex import Multiplex
from coffee.io.scale import Scale
from coffee.app.app import LCDApp

lcd = LCDApp()

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
    smoothing_method="median",
    smoothing_window=5,
)

lcd.set_inputs(scale=scale, multiplex=multiplex, encoder=encoder)
lcd.display()

try:
    scale.start_reading()
    while True:
        multiplex.mcp.digital_read_all()
        lcd.check_timeout()
        time.sleep(1)
except Exception as e:
    raise e
finally:
    scale.stop_reading()
