import time
import signal

from inputs.encoder import Encoder
from inputs.multiplex import MultiPlex
from scale.scale import Scale
from ui.app import LCDApp

def valueChanged(value, direction):
    print("* New value: {}, Direction: {}".format(value, direction))

lcd = LCDApp()

encoder = Encoder(
    clk_pin=26,
    data_pin=21,
    encoder_button_pin=20,
    red_button_pin=18,
    encoder_callback=lcd.encoder_callback,
    encoder_button_callback=lcd.encoder_button_callback,
    red_button_callback=lcd.red_button_callback,
)

multiplex = MultiPlex(
    interrupt_pin=4,
    button_callback=lcd.person_button_callback,
)

scale = Scale(
    smoothing_method="median", 
    smoothing_window=5,
    served_mug_callback=lcd.served_mug_callback,
    removed_pot_callback=lcd.removed_pot_callback,
)

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
