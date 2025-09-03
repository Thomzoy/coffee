"""LCD application orchestration module.

This module defines the main application `LCDApp` which
coordinates the LCD display, input devices (rotary encoder, buttons through
multiplexer) and the scale events to provide an interactive coffee tracking
user interface.

All page transitions are centralized through the `set_page` decorator in
order to guarantee consistent refresh, power management (turn on) and timeout
reset.
"""

from functools import wraps
from time import time
from typing import Any, Callable, List, Optional

from coffee.app.page import BasePage, MugPage, Page
from coffee.config import MUG_BUTTON_LOOKBEHIND_DURATION, DEFAULT_LCD_TIMEOUT
from coffee.io.encoder import Encoder
from coffee.io.lcd import LCD
from coffee.io.multiplex import Multiplex
from coffee.io.scale import Scale


def set_page(func: Callable[..., Optional[Page]]) -> Callable[..., Optional[Page]]:
    """Decorator to handle page transitions in the LCD app.

    The decorated callback may return a new `Page` instance (or
    `None` to remain on the current page). This decorator centralizes the
    logic to:

    1. Attach the LCD reference to the newly returned page
    2. Turn the LCD on (it may have been turned off after a timeout)
    3. Trigger a display refresh
    4. Update the last interaction timestamp
    """

    @wraps(func)
    def wrapper(self: "LCDApp", *args: Any, **kwargs: Any) -> Optional[Page]:
        page = func(self, *args, **kwargs)
        if page is not None:
            self.page = page.set_lcd(self.lcd)
        self.lcd.turn_on()
        self.page.display()
        self.last_update = int(time())
        return page

    return wrapper


class LCDApp:
    """Main LCD application controller.

    This class brings together:

    * The physical LCD (`LCD` instance)
    * Optional input devices (rotary encoder, button multiplexer, scale)
    * A stateful `Page` hierarchy for UI navigation

    It also enforces inactivity timeouts to revert to the base page and powers
    down the LCD after a period of no interaction.
    """

    def __init__(
        self,
        address: int = 0x27,
        rows: int = 2,
        width: int = 16,
        page: Optional[Page] = None,
        timeout: int = DEFAULT_LCD_TIMEOUT,
    ) -> None:
        """Initialize the LCD application.

        Parameters
        ----------
        address:
            I2C address of the LCD backpack.
        rows:
            Number of visible rows (typically 2 or 4).
        width:
            Number of characters per row.
        page:
            Initial page instance (defaults to a new `BasePage`).
        timeout:
            Global inactivity timeout (seconds) used when a page does not
            define its own ``timeout`` attribute.
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
    ) -> None:
        """Configure optional hardware input devices.

        Each provided device will have its callbacks registered so that UI
        navigation and events (mug served, pot removed, button presses, rotary
        turns) are routed through the application and page layer.

        Parameters
        ----------
        scale:
            Optional `Scale` instance used to detect pot removal / mug serving.
        multiplex:
            Optional `Multiplex` instance for person buttons.
        encoder:
            Optional `Encoder` instance for navigation and validation.
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
            self.encoder.set_encoder_callback(self.encoder_callback)
            self.encoder.set_encoder_button_callback(self.encoder_button_callback)
            self.encoder.set_red_button_callback(self.red_button_callback)

    def display(self) -> None:
        """Refresh the LCD with the current page content."""
        self.lcd.clear()
        self.page.display()

    def check_timeout(self) -> None:
        """Check page timeout and revert to base page / power-saving mode.

        If the active page defines a ``timeout`` attribute it's used;
        otherwise the application-wide default timeout is applied.
        """
        # Pages may optionally define a "timeout" attribute (in seconds)
        timeout: int = getattr(self.page, "timeout", self.timeout) or self.timeout
        if int(time()) - self.last_update >= timeout:
            self.page.timeout_callback()
            if not isinstance(self.page, BasePage):
                print("Timeout")
                self.lcd.turn_off()
                self.page = BasePage().set_lcd(self.lcd)
                self.page.display()

    @set_page
    def encoder_callback(self, clockwise: bool) -> Optional[Page]:
        """Rotary encoder rotation event.

        Parameters
        ----------
        clockwise:
            ``True`` if the physical rotation is clockwise, else counterclockwise.
        """
        print(f"Encoder - Clockwise {clockwise} - Page {self.page.__class__.__name__}")
        return self.page.encoder_callback(clockwise)

    @set_page
    def encoder_button_callback(self) -> Optional[Page]:
        """Rotary encoder push button event."""
        print(f"Encoder button - Page {self.page.__class__.__name__}")
        return self.page.encoder_button_callback()

    @set_page
    def red_button_callback(self) -> Optional[Page]:
        """Red (cancel) button event."""
        print(f"Red button - Page {self.page.__class__.__name__}")
        return self.page.red_button_callback()

    @set_page
    def person_button_callback(self, button_id: int) -> Optional[Page]:
        """Person button event.

        Parameters
        ----------
        button_id:
            Zero-based index of the pressed person button.
        """
        print(
            f"Person button callback - ID {button_id} - Page {self.page.__class__.__name__}"
        )
        return self.page.person_button_callback(button_id)

    @set_page
    def served_mug_callback(self, mug_value: float) -> Optional[Page]:
        """A new mug has been detected by the scale.

        Parameters
        ----------
        mug_value:
            Mug weight in grams reported by the scale.
        """
        print(f"New mug - {mug_value} g")
        recent_button_presses: List[int] = []
        if MUG_BUTTON_LOOKBEHIND_DURATION and self.multiplex is not None:
            # Gather button presses that occurred within the look-behind window
            now = time()
            recent_button_presses = [
                person_id
                for person_id, timestamp in self.multiplex.state.items()
                if now - timestamp < MUG_BUTTON_LOOKBEHIND_DURATION
            ]
            if recent_button_presses:
                print(f"Including: {recent_button_presses}")
        return MugPage(mug_value=mug_value, person_ids=recent_button_presses)

    @set_page
    def removed_pot_callback(self) -> Optional[Page]:
        """Pot removed event (start of serving workflow)."""
        print("Pot removed")
        return MugPage()
