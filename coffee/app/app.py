from time import time
from typing import Optional

import wrapt

from coffee.io.lcd import LCD

from .page import BasePage, MugPage, Page


@wrapt.decorator
def set_page(wrapped, instance, args, kwargs):
    # Call the original method
    page = wrapped(*args, **kwargs)

    # Only proceed if this is an instance method
    if page is not None:
        instance.lcd.display_on()
        instance.lcd.backlight_on()
        instance.page = page.set_lcd(instance.lcd)
    instance.lcd.clear()
    instance.page.display()
    instance.last_update = int(time())

    return page


class LCDApp:
    def __init__(
        self,
        address: int = 0x27,
        rows: int = 2,
        width: int = 16,
        page: Optional[Page] = None,
        timeout: int = 15,
    ):
        self.lcd = LCD(1, address, rows, width)
        self.page = page if page is not None else BasePage().set_lcd(self.lcd)
        self.timeout = timeout
        self.last_update = int(time())

    def display(self):
        self.lcd.clear()
        self.page.display()

    def check_timeout(self):
        if not isinstance(self.page, BasePage):
            if int(time()) - self.last_update >= self.timeout:
                print("Timeout")
                self.page.timeout_callback()
                self.lcd.clear()
                self.lcd.display_off()
                self.lcd.backlight_off()
                self.page = BasePage().set_lcd(self.lcd)
                self.page.display()

    @set_page
    def encoder_callback(self, clockwise: bool):
        print(f"Encoder - Clockwise {clockwise} - Page {self.page.__class__.__name__}")
        return self.page.encoder_callback(clockwise)

    @set_page
    def encoder_button_callback(self):
        print(f"Encoder button - Page {self.page.__class__.__name__}")
        return self.page.encoder_button_callback()

    @set_page
    def red_button_callback(self):
        print(f"Red button - Page {self.page.__class__.__name__}")
        return self.page.red_button_callback()

    @set_page
    def person_button_callback(self, button_id):
        print(
            f"Person button callback - ID {button_id} - Page {self.page.__class__.__name__}"
        )
        return self.page.person_button_callback(button_id)

    @set_page
    def served_mug_callback(self, mug_value: float):
        print(f"New mug - {mug_value} g")
        return MugPage(mug_value=mug_value)

    @set_page
    def removed_pot_callback(self):
        return MugPage()
