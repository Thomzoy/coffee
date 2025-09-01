from time import time
from typing import Dict, Optional

import wrapt

from coffee.io.lcd import LCD
from coffee.io.encoder import Encoder
from coffee.io.multiplex import Multiplex
from coffee.io.scale import Scale
from coffee.app.page import BasePage, MugPage, Page

from coffee.config import MUG_BUTTON_LOOKBEHIND_DURATION


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
        self.scale: Scale | None = None
        self.multiplex: Multiplex | None = None
        self.encoder: Encoder | None = None

    def set_inputs(
        self,
        scale: Scale | None = None,
        multiplex: Multiplex | None = None,
        encoder: Encoder | None = None,
    ):
        if scale is not None:
            self.scale = scale
            self.scale.set_served_mug_callback(self.served_mug_callback)
            self.scale.set_removed_pot_callback(self.removed_pot_callback)

        if multiplex is not None:
            self.multiplex = multiplex
            self.multiplex.set_button_callback(self.person_button_callback)

        if encoder is not None:
            self.encoder = encoder
            self.encoder.set_encoder_callback(self.encoder_callback),
            self.encoder.set_encoder_button_callback(self.encoder_button_callback),
            self.encoder.set_red_button_callback(self.red_button_callback),

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
        if MUG_BUTTON_LOOKBEHIND_DURATION:
            now = time()
            recent_button_presses = set([
                person_id for person_id, timestamp in self.multiplex.state.items() if now - timestamp < MUG_BUTTON_LOOKBEHIND_DURATION
            ])
            print(f"Including: {recent_button_presses}")
        return MugPage(mug_value=mug_value, person_ids=recent_button_presses)

    @set_page
    def removed_pot_callback(self):
        return MugPage()
