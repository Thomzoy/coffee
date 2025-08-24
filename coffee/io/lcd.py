import threading
import time

import wrapt
from lcd.i2c_lcd import I2cLcd

from coffee.config import CUSTOM_CHARS


@wrapt.decorator
def single_lcd_write(wrapped, instance, args, kwargs):
    # Kill any LCD writing thread
    if hasattr(instance, "lcd"):
        instance = instance.lcd
    if hasattr(instance, "lcd_thread"):
        # Stop any currently running scroll thread
        if instance.lcd_thread and instance.lcd_thread.is_alive():
            instance.stop_event.set()
            instance.lcd_thread.join()
        # Clear the stop flag for the new thread
        instance.stop_event.clear()

    return wrapped(*args, **kwargs)


class LCD(I2cLcd):
    def __init__(
        self,
        port: int = 1,
        i2c_addr: int = 0x27,
        num_lines: int = 16,
        num_columns: int = 2,
    ):
        super().__init__(port, i2c_addr, num_lines, num_columns)

        self.lcd_thread = None
        self.stop_event = threading.Event()

        self.register_custom_characters()

    def register_custom_characters(self):
        for idx, (name, array) in enumerate(CUSTOM_CHARS.items()):
            if idx < 8:  # 8 addresses available
                self.custom_char(idx, array)

    def check_thread(self):
        # Stop any currently running scroll thread
        if self.lcd_thread and self.lcd_thread.is_alive():
            self.stop_event.set()
            self.lcd_thread.join()

        # Clear the stop flag for the new thread
        self.stop_event.clear()

    @single_lcd_write
    def scroll_message(self, message: str, row: int = 0, sleep: float = 0.5):
        # self.check_thread()

        # Start a new scrolling thread
        def worker():
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

    @single_lcd_write
    def blink(self, interval: float = 0.5, n: int = -1):
        # self.check_thread()
        def worker():
            self.move_to(0, 0)
            self.putstr("Service ...")
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
    def clear(self):
        super().clear()
