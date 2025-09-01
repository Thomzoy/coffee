from time import time
from typing import Any, Callable, Optional

import wrapt

from coffee.app.page import BasePage, MugPage, Page
from coffee.config import MUG_BUTTON_LOOKBEHIND_DURATION
from coffee.io.encoder import Encoder
from coffee.io.lcd import LCD
from coffee.io.multiplex import Multiplex
from coffee.io.scale import Scale


@wrapt.decorator
def set_page(
    wrapped: Callable, instance: Any, args: tuple, kwargs: dict
) -> Optional[Page]:
    """
    Decorator to handle page transitions in the LCD app.

    Updates the display, sets the new page, and refreshes the screen.

    Args:
        wrapped: The function being decorated
        instance: The LCDApp instance
        args: Positional arguments for the wrapped function
        kwargs: Keyword arguments for the wrapped function

    Returns:
        The new page or None
    """
    # Call the original method
    page = wrapped(*args, **kwargs)

    if page is not None:
        instance.lcd.display_on()
        instance.lcd.backlight_on()
        instance.page = page.set_lcd(instance.lcd)
    instance.lcd.clear()
    instance.page.display()
    instance.last_update = int(time())

    return page


class LCDApp:
    """
    Main LCD application controller.

    Manages the LCD display, user input, and page navigation for the coffee machine interface.
    """

    def __init__(
        self,
        address: int = 0x27,
        rows: int = 2,
        width: int = 16,
        page: Optional[Page] = None,
        timeout: int = 15,
    ):
        """
        Initialize the LCD application.

        Args:
            address: I2C address of the LCD
            rows: Number of rows on the LCD
            width: Number of columns on the LCD
            page: Initial page to display (defaults to BasePage)
            timeout: Timeout in seconds for automatic page reset
        """
        self.lcd = LCD(1, address, rows, width)
        self.page = page if page is not None else BasePage().set_lcd(self.lcd)
        self.timeout = timeout
        self.last_update = int(time())
        self.is_on = True
        self.scale: Scale | None = None
        self.multiplex: Multiplex | None = None
        self.encoder: Encoder | None = None

    def set_inputs(
        self,
        scale: Scale | None = None,
        multiplex: Multiplex | None = None,
        encoder: Encoder | None = None,
    ):
        """
        Configure input devices for the LCD app.

        Args:
            scale: Weight scale sensor
            multiplex: Button multiplexer
            encoder: Rotary encoder with buttons
        """
        if scale is not None:
            self.scale = scale
            self.scale.set_served_mug_callback(self.served_mug_callback)
            self.scale.set_removed_pot_callback(self.removed_pot_callback)

        if multiplex is not None:
            self.multiplex = multiplex
            self.multiplex.set_button_callback(self.person_button_callback)

        if encoder is not None:
            self.encoder = encoder
            (self.encoder.set_encoder_callback(self.encoder_callback),)
            (self.encoder.set_encoder_button_callback(self.encoder_button_callback),)
            (self.encoder.set_red_button_callback(self.red_button_callback),)

    def display(self):
        """Refresh the LCD display with the current page content."""
        self.lcd.clear()
        self.page.display()

    def check_timeout(self):
        """Check if the current page has timed out and reset to base page if needed."""
        if int(time()) - self.last_update >= self.timeout:
            self.page.timeout_callback()
            if not isinstance(self.page, BasePage):
                print("Timeout")
                self.lcd.turn_off()
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
            recent_button_presses = [
                person_id
                for person_id, timestamp in self.multiplex.state.items()
                if now - timestamp < MUG_BUTTON_LOOKBEHIND_DURATION
            ]
            print(f"Including: {recent_button_presses}")
        return MugPage(mug_value=mug_value, person_ids=recent_button_presses)

    @set_page
    def removed_pot_callback(self):
        return MugPage()
