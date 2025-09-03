import threading
import time
from typing import Any, Callable, Optional

import wrapt
from lcd.i2c_lcd import I2cLcd

from coffee.config import CUSTOM_CHARS


@wrapt.decorator
def single_lcd_write(
    wrapped: Callable, instance: Any, args: tuple, kwargs: dict
) -> Any:
    """
    Decorator to ensure single LCD write operations by managing LCD threads.

    Stops any running LCD thread before executing the wrapped function and
    clears the stop event for new threads.

    Args:
        wrapped: The function being decorated
        instance: The instance the method is called on
        args: Positional arguments for the wrapped function
        kwargs: Keyword arguments for the wrapped function

    Returns:
        The result of the wrapped function
    """
    # Kill any LCD writing thread
    if hasattr(instance, "lcd"):
        instance = instance.lcd
    if hasattr(instance, "lcd_thread"):
        # Stop any currently running scroll thread
        if instance.lcd_thread and instance.lcd_thread.is_alive():
            print("has thread")
            instance.stop_event.set()
            instance.lcd_thread.join()
            time.sleep(0.2)
        # Clear the stop flag for the new thread
        instance.stop_event.clear()

    return wrapped(*args, **kwargs)


class LCD(I2cLcd):
    """
    Enhanced LCD class with scrolling and blinking capabilities.

    Extends I2cLcd with thread-safe scrolling messages and blinking functionality.
    """

    def __init__(
        self,
        port: int = 1,
        i2c_addr: int = 0x27,
        num_lines: int = 16,
        num_columns: int = 2,
    ) -> None:
        """
        Initialize the LCD with enhanced capabilities.

        Args:
            power_pin: set if a MOSFET powers the device
            port: I2C port number
            i2c_addr: I2C address of the LCD
            num_lines: Number of lines on the LCD
            num_columns: Number of columns on the LCD
        """
        super().__init__(port, i2c_addr, num_lines, num_columns)

        self.lcd_thread = None
        self.stop_event = threading.Event()

        self.register_custom_characters()

    def register_custom_characters(self) -> None:
        """Register custom characters from the configuration."""
        for idx, (name, array) in enumerate(CUSTOM_CHARS.items()):
            if idx < 8:  # 8 addresses available
                self.custom_char(idx, array)

    @single_lcd_write
    def scroll_message(self, message: str, row: int = 0, sleep: float = 0.5) -> None:
        """
        Display a scrolling message on the specified row.

        Args:
            message: The message to scroll
            row: The row number to display on (0 or 1)
            sleep: Time in seconds between scroll steps
        """

        # Start a new scrolling thread
        def worker() -> None:
            self.hide_cursor()
            self.blink_cursor_off()
            self.hide_cursor()
            self.move_to(0, row)

            n = 15
            tmp_message = (n + 1) * " " + message + (n + 1) * " "

            for idx in range(n + 2 + len(message)):
                if self.stop_event.is_set():
                    print("Done scroll")
                    break  # Stop immediately if a new message comes in

                self.move_to(0, row)
                self.putstr(tmp_message[idx : idx + n])
                time.sleep(sleep)

        self.lcd_thread = threading.Thread(target=worker, daemon=True)
        self.lcd_thread.start()

    #@single_lcd_write
    def blink(self, message:str, interval: float = 0.5, n: int = -1) -> None:
        """
        Blink the LCD backlight with a service message.

        Args:
            interval: Time in seconds between blinks
            n: Number of blinks (-1 for infinite)
        """

        def worker() -> None:
            self.move_to(0, 0)
            self.putstr(message)
            idx = 0
            while True:
                if self.stop_event.is_set() or ((n > 0) and (idx >= n)):
                    self.backlight_on()
                    print("Done blink")
                    break
                self.backlight_on() if idx % 2 else self.backlight_off()
                idx += 1
                time.sleep(interval)

        self.lcd_thread = threading.Thread(target=worker, daemon=True)
        self.lcd_thread.start()

    @single_lcd_write
    def turn_off(self):
        self.clear()
        self.display_off()
        self.backlight_off()

    @single_lcd_write
    def turn_on(self):
        self.clear()
        self.display_on()
        self.backlight_on()

    @single_lcd_write
    def clear(self) -> None:
        super().clear()
