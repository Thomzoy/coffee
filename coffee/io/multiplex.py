import time
from typing import Callable, Dict, List, Optional

import smbus
from gpiozero import Button, Device
from gpiozero.pins.pigpio import PiGPIOFactory
from mcp23017 import *
from mcp23017.i2c import I2C

from coffee.app.page import Page

Device.pin_factory = PiGPIOFactory()


class Multiplex:
    """
    MCP23017-based button multiplexer with interrupt handling.

    Manages multiple button inputs through an I2C multiplexer with
    interrupt-driven event detection.
    """

    def __init__(
        self,
        address: int = 0x20,
        interrupt_pin: int = 4,
        button_callback: Optional[Callable[[int], Page | None]] = None,
    ):
        self.button = Button(interrupt_pin, pull_up=True, bounce_time=0.2)
        self.i2c = I2C(smbus.SMBus(1))
        self.mcp = MCP23017(address, self.i2c.bus)

        # Set all as input
        self.mcp.set_all_input()

        # Enable internal pull-up resistors
        self.mcp.write(GPPUA, 0xFF)
        self.mcp.write(GPPUB, 0xFF)

        # Set interrupt comparison to default values
        self.mcp.write(GPINTENA, 0xFF)
        self.mcp.write(GPINTENB, 0xFF)

        # Set default value to compare against (all HIGH)
        self.mcp.write(DEFVALA, 0xFF)
        self.mcp.write(DEFVALB, 0xFF)

        # Compare to DEFVAL instead of previous value
        self.mcp.write(INTCONA, 0xFF)
        self.mcp.write(INTCONB, 0xFF)

        # Enable interrupt mirroring
        self.mcp.set_interrupt_mirror(True)

        # Enable open-drain for interrupt output pin
        self.mcp.set_bit_enabled(IOCONA, ODR_BIT, True)
        self.mcp.set_bit_enabled(IOCONB, ODR_BIT, True)

        # Stores the time of last button press:
        self.state: Dict[int, int] = dict()

        self.button_callback = button_callback
        self.button.when_pressed = self.interrupt_callback

        # Store captures:
        self.caps_a = None
        self.caps_b = None

    def cleanup(self):
        self.button.close()

    def get_pressed_button_id(
        self, 
        flags_a: List[str], flags_b: List[str],
        caps_a: List[str], caps_b: List[str]
    ) -> Optional[int]:

        if self.caps_a is not None:
            # Interrupt on A occured at least once before, we can use this registry
            indices = [i==j for (i,j) in zip(self.caps_a, caps_a)]

        flags = flags_a + flags_b
        try:
            return flags.index("1")
        except ValueError:
            print("No button was pressed")
            return None

    def interrupt_callback(self) -> None:
        """
        Handle MCP23017 interrupt events for button presses.

        Reads interrupt flags, determines which button was pressed,
        and triggers the configured callback.
        """
        flags_a, flags_b = self.mcp.read_interrupt_flags()
        caps_a, caps_b = self.mcp.read_interrupt_captures()
        print(flags_a, caps_a)
        print(flags_b, caps_b)
        pressed_id = self.get_pressed_button_id(flags_a, flags_b, caps_a, caps_b)
        print("Pressed: ", pressed_id)

        # Reset interrupt by reading all pins
        self.mcp.digital_read_all()

        if pressed_id is not None:
            self.state[pressed_id] = int(time.time())
            if self.button_callback is not None:
                self.button_callback(pressed_id)

    def set_button_callback(
        self, button_callback: Optional[Callable[[int, Dict[int, int]], Page | None]]
    ):
        self.button_callback = button_callback
