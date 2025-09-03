"""Rotary encoder input abstraction.

Provides a higher-level interface around GPIO events for a quadrature rotary
encoder plus two push buttons (encoder button + red/cancel button). External
callbacks can be registered to react to rotations or button presses.
"""

from typing import Optional, Protocol

from gpiozero import Button, Device
from gpiozero.pins.pigpio import PiGPIOFactory

from coffee.app.page import Page

Device.pin_factory = PiGPIOFactory()


class RotationCallback(Protocol):
    def __call__(self, clockwise: bool) -> Optional[Page]: ...  # pragma: no cover


class ButtonCallback(Protocol):
    def __call__(self) -> Optional[Page]: ...  # pragma: no cover


class Encoder:
    """
    Rotary encoder with button interface for user input.

    Handles rotary encoder rotation detection and button press events
    using GPIO pins and callbacks.
    """

    def __init__(
        self,
        clk_pin: int,
        data_pin: int,
        encoder_button_pin: Optional[int] = None,
        red_button_pin: Optional[int] = None,
        encoder_callback: Optional[RotationCallback] = None,
        encoder_button_callback: Optional[ButtonCallback] = None,
        red_button_callback: Optional[ButtonCallback] = None,
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

        # Classical buttons
        self.encoder_button = Button(encoder_button_pin, pull_up=True, bounce_time=0.05)
        if encoder_button_callback:
            self.encoder_button.when_pressed = encoder_button_callback

        self.red_button = Button(red_button_pin, pull_up=True, bounce_time=0.05)
        if red_button_callback:
            self.red_button.when_pressed = red_button_callback

    def cleanup(self):
        self.clk_pin.close()
        self.data_pin.close()
        self.encoder_button.close()
        self.red_button.close()

    def transition(self) -> None:
        """
        Handle encoder state transitions and detect rotation direction.

        Processes GPIO pin state changes to determine clockwise or
        counterclockwise rotation based on quadrature encoding.
        """
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

    def get_value(self) -> int:
        """Return the raw internal value (currently unused incrementally)."""
        return self.value

    def set_encoder_callback(
        self, encoder_callback: Optional[RotationCallback]
    ) -> None:
        self.encoder_callback = encoder_callback

    def set_encoder_button_callback(
        self, encoder_button_callback: Optional[ButtonCallback]
    ) -> None:
        self.encoder_button.when_pressed = encoder_button_callback

    def set_red_button_callback(
        self, red_button_callback: Optional[ButtonCallback]
    ) -> None:
        self.red_button.when_pressed = red_button_callback
