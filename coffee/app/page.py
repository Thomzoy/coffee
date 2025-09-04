"""UI page hierarchy for the LCD application.

Each concrete subclass of :class:`Page` encapsulates the behaviour and
presentation of a particular state of the LCD interface (home page, menu,
person info, mug serving workflow, etc.). Pages may return a new page object
from any callback method to trigger a navigation transition.
"""

import subprocess
import time
from datetime import datetime
from typing import List, Optional

from coffee.config import CUSTOM_CHARS_IDX
from coffee.io.lcd import LCD, single_lcd_write

from .db import Database


class Page:
    """Base class for LCD application pages.

    Subclasses can override any of the input callback methods to implement
    navigation or behaviour. To trigger a page transition simply return a new
    `Page` instance; returning `None` keeps the current page (but will
    refresh it by running `.display()`).
    """

    def __init__(
        self,
    ):
        """Initialize a new page."""
        pass

    def set_lcd(self, lcd: LCD) -> "Page":
        """Associate this page with an LCD instance and return self."""
        self.lcd = lcd
        return self

    @single_lcd_write  # type: ignore[misc]
    def display(self) -> None:
        self.lcd.move_to(0, 0)
        self.lcd.putstr("My Page")

    @single_lcd_write  # type: ignore[misc]
    def display_temporary(
        self,
        first_line: Optional[str] = None,
        second_line: Optional[str] = None,
        duration: int = 1,
    ) -> None:
        """Temporarily display one or two lines then pause.

        Parameters
        ----------
        first_line:
            Text for line 0.
        second_line:
            Text for line 1 (optional).
        duration:
            Time in seconds to keep the message visible.
        """
        self.lcd.clear()
        if first_line is not None:
            self.lcd.move_to(0, 0)
            self.lcd.putstr(first_line)
        if second_line is not None:
            self.lcd.move_to(0, 1)
            self.lcd.putstr(second_line)

        time.sleep(duration)

    def timeout_callback(self) -> Optional["Page"]:
        return self.red_button_callback()

    def encoder_callback(self, clockwise: bool) -> Optional["Page"]:
        pass

    def encoder_button_callback(self) -> Optional["Page"]:
        pass

    def red_button_callback(self) -> Optional["Page"]:
        print("Retour ...")
        self.display_temporary("Retour ...")
        return HomePage()

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        pass


class HomePage(Page):
    """Default home page displayed when the application starts or times out."""

    def __init__(self):
        super().__init__()
        #self.has_timed_out = False

    @single_lcd_write  # type: ignore[misc]
    def display(self) -> None:
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Bonjour !")

    def encoder_callback(self, clockwise: bool) -> Optional["Page"]:
        return MenuPage()

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        return PersonPage(button_id)

    def timeout_callback(self) -> Optional["Page"]:
        #if not self.has_timed_out:
            #self.has_timed_out = True
        self.lcd.turn_off()


class NameButtonPage(Page):
    """Interactive page for assigning human-readable names to buttons."""

    values = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + [CUSTOM_CHARS_IDX["enter"]]

    def __init__(self):
        super().__init__()
        self.button_id = None
        self.name = ""
        self.encoder_idx = 0

    @single_lcd_write  # type: ignore[misc]
    def display(self) -> None:
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        if not self.button_id:
            self.lcd.putstr("Quel bouton ?")
        else:
            self.lcd.putstr(f"{self.button_id} - Quel nom ?")
            self.lcd.move_to(0, 1)
            self.lcd.putstr(self.name)
            self.lcd.putchar(self.values[self.encoder_idx])

    def encoder_callback(self, clockwise: bool) -> Optional["Page"]:
        increment = 1 if clockwise else -1
        self.encoder_idx = (self.encoder_idx + increment) % len(self.values)

    def encoder_button_callback(self) -> Optional["Page"]:
        """Save name"""
        value = self.values[self.encoder_idx]
        if (
            (value == CUSTOM_CHARS_IDX["enter"])
            and self.name
            and (self.button_id is not None)
        ):
            print("Enter")
            with Database() as db:
                db.add_user(button_id=self.button_id, name=self.name)
                self.display_temporary("Nom enregistre:", self.name)
            return MenuPage()
        else:
            self.name += value
            self.encoder_idx = 0

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        self.button_id = button_id


class PersonPage(Page):
    """Display personalised greeting and consumption statistics for a user."""

    def __init__(self, button_id: int):
        super().__init__()
        self.button_id = button_id

    @single_lcd_write  # type: ignore[misc]
    def display(self) -> None:
        with Database() as db:
            name = db.get_name(self.button_id)
            mugs = db.get_mugs(name)
        self.lcd.move_to(0, 0)
        self.lcd.putstr(f"{name}:")
        self.lcd.move_to(0, 1)

        mugs_today = [
            mug for mug in mugs if mug["datetime"].date() == datetime.now().date()
        ]
        n = len(mugs_today)
        mug_str = "tasse" if n < 2 else "tasses"
        volume_today = sum(mug["value"] for mug in mugs_today)

        message = f"Ajd: {n} {mug_str} - {int(volume_today)} mL"
        self.lcd.scroll_message(message, row=1, sleep=0.2)

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        self.button_id = button_id


class MugPage(Page):
    """Handle mug serving workflow, weight assignment and validation."""

    def __init__(
        self, mug_value: Optional[float] = None, person_ids: Optional[List[int]] = None
    ):
        super().__init__()
        self.mug_value = mug_value
        self.person_ids = person_ids if person_ids is not None else []
        self.timeout = 5  # shorter timeout here

    @single_lcd_write
    def display(self) -> None:
        if self.mug_value is None:
            # Pot is removed
            print("Service...")
            self.lcd.blink("Service...")

        else:
            self.lcd.move_to(0, 0)
            self.lcd.putstr(f"{int(self.mug_value)}mL - Pour ?")

            if self.person_ids:
                with Database() as db:
                    names = [str(db.get_name(person_id)) for person_id in self.person_ids]
                message = " + ".join(names)
                self.lcd.scroll_message(message, row=1, sleep=0.15)

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        if button_id not in self.person_ids:
            self.person_ids.append(str(button_id))

    def encoder_button_callback(self) -> Optional["Page"]:
        if self.mug_value is not None:
            with Database() as db:
                for person_id in self.person_ids:
                    db.add_mug(person_id, self.mug_value / len(self.person_ids))
            self.display_temporary("OK !", duration=2)
        return HomePage()

    def red_button_callback(self) -> Optional["Page"]:
        # Remove all person recorded for the current mug (if any)
        # Else, back to main page
        if self.person_ids:
            self.person_ids = self.person_ids[:-1]
        else:
            self.display_temporary("Annule tasse...")
            return HomePage()

    def timeout_callback(self) -> Optional["Page"]:
        if self.person_ids:
            self.encoder_button_callback()


class ShutdownPage(Page):
    """Page used to trigger system shutdown or restart."""

    def __init__(self, restart: bool = False):
        self.restart = restart

    @single_lcd_write
    def display(self) -> None:
        if self.restart:
            self.display_temporary("Restart ...", duration=2)
            subprocess.check_output("sudo shutdown -r now", shell=True, text=True)
        else:
            self.display_temporary("Shutdown ...", duration=2)
            self.lcd.turn_off()
            subprocess.check_output("sudo shutdown -h now", shell=True, text=True)

class HostnamePage(Page):
    """Show hostname"""

    @single_lcd_write
    def display(self) -> None:
        try:
            message = subprocess.check_output("hostname -I", shell=True, text=True).strip()
        except subprocess.CalledProcessError as e:
            message = f"Error {e.returncode}"
        self.display_temporary("Hostname:", message, duration=10)

class StatsPage(Page):
    """Display aggregated statistics (total mugs and volume)."""

    def __init__(self):
        with Database() as db:
            self.stats = db.get_sum()

    @single_lcd_write
    def display(self) -> None:
        self.display_temporary(
            f"{self.stats['count']} tasses",
            f"{1e-3 * self.stats['sum']:.2f} L",
        )


class MenuPage(Page):
    """Main menu listing administrative / utility pages."""

    PAGES = [
        dict(name="Nommer bouton", page=NameButtonPage()),
        dict(name="Stats", page=StatsPage()),
        dict(name="Host name", page=HostnamePage()),
        dict(name="Eteindre", page=ShutdownPage()),
        dict(name="Redemarrer", page=ShutdownPage(restart=True)),
    ]

    def __init__(self):
        super().__init__()
        self.encoder_idx = 0

    @single_lcd_write
    def display(self) -> None:
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Menu...")
        self.lcd.move_to(0, 1)
        self.lcd.putstr(self.PAGES[self.encoder_idx]["name"])

    def encoder_callback(self, clockwise: bool) -> Optional["Page"]:
        increment = 1 if clockwise else -1
        self.encoder_idx = (self.encoder_idx + increment) % len(self.PAGES)

    def encoder_button_callback(self) -> Optional["Page"]:
        return self.PAGES[self.encoder_idx]["page"]
