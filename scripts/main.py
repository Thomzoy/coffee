#! /home/dietpi/coffee/.venv//bin/activate

import signal
from threading import Event

from coffee.app.app import LCDApp
from coffee.io.encoder import Encoder
from coffee.io.multiplex import Multiplex
from coffee.io.scale import Scale

if __name__ == "__main__":
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

    scale = Scale()

    app.set_inputs(scale=scale, multiplex=multiplex, encoder=encoder)
    app.display()

    exit = Event()

    def quit(signo, _frame):
        print(f"Interrupted by {signo}, shutting down")
        exit.set()

    signal.signal(signal.SIGTERM, quit)
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGHUP, quit)

    try:
        scale.start_reading()
        while not exit.is_set():
            scale.read()
            multiplex.mcp.digital_read_all()
            app.check_timeout()
            exit.wait(0.5)
    except Exception as e:
        raise e
    finally:
        print("Scale cleanup")
        scale.stop_reading()
        print("Multiplex cleanup")
        multiplex.cleanup()
        print("Encoder cleanup")
        encoder.cleanup()
        print("LCD cleanup")
        app.lcd.turn_off()
