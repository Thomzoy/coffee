from typing import Callable, Optional

from gpiozero import Button, Device
from gpiozero.pins.pigpio import PiGPIOFactory

Device.pin_factory = PiGPIOFactory()


class Encoder:
    def __init__(
        self,
        clk_pin: int,
        data_pin: int,
        encoder_button_pin: Optional[int] = None,
        red_button_pin: Optional[int] = None,
        encoder_callback: Optional[Callable[[bool], None]] = None,
        encoder_button_callback: Optional[Callable[[], None]] = None,
        red_button_callback: Optional[Callable[[], None]] = None,
    ):
        # Rotary encoder pins (pulldown)
        self.clk_pin = Button(clk_pin, pull_up=False)
        self.data_pin = Button(data_pin, pull_up=False)

        self.value = 0
        self.state = "00"
        self.direction = None
        self.encoder_callback = encoder_callback

        # Register encoder event handlers
        self.clk_pin.when_pressed = self.transition
        self.clk_pin.when_released = self.transition
        self.data_pin.when_pressed = self.transition
        self.data_pin.when_released = self.transition

        # Optional classical buttons (pull-up)
        self.encoder_button = None
        self.red_button = None

        if encoder_button_pin is not None:
            self.encoder_button = Button(
                encoder_button_pin, pull_up=True, bounce_time=0.05
            )
            if encoder_button_callback:
                self.encoder_button.when_pressed = lambda: encoder_button_callback()

        if red_button_pin is not None:
            self.red_button = Button(red_button_pin, pull_up=True, bounce_time=0.05)
            if red_button_callback:
                self.red_button.when_pressed = lambda: red_button_callback()

    def transition(self):
        p1 = int(self.clk_pin.is_pressed)
        p2 = int(self.data_pin.is_pressed)
        newState = f"{p1}{p2}"

        # (state, newState) -> direction
        mapping = {
            ("00", "01"): "R",
            ("00", "10"): "L",
            ("01", "11"): "R",
            ("01", "00"): "L",
            ("10", "11"): "L",
            ("10", "00"): "R",
        }
        self.direction = mapping.get((self.state, newState))
        if self.direction and (newState == "00") and self.encoder_callback:
            self.encoder_callback(self.direction == "L")
        self.state = newState

    def get_value(self):
        return self.value

    def set_encoder_callback(self, encoder_callback: Optional[Callable[[bool], None]]):
        self.encoder_callback = encoder_callback

    def set_encoder_button_callback(
        self, encoder_button_callback: Optional[Callable[[], None]]
    ):
        self.encoder_button_callback = encoder_button_callback

    def set_red_button_callback(
        self, red_button_callback: Optional[Callable[[], None]]
    ):
        self.red_button_callback = red_button_callback
