import time
from datetime import datetime
from typing import Optional

from coffee.config import CUSTOM_CHARS_IDX
from coffee.io.lcd import LCD, single_lcd_write

from .db import Database


class Page:
    def __init__(
        self,
    ):
        pass

    def set_lcd(self, lcd: LCD):
        self.lcd = lcd
        return self

    @single_lcd_write
    def display(self):
        self.lcd.move_to(0, 0)
        self.lcd.putstr("My Page")

    @single_lcd_write
    def display_temporary(
        self,
        first_line: Optional[str] = None,
        second_line: Optional[str] = None,
        duration: int = 1,  # in s
    ):
        self.lcd.clear()
        if first_line is not None:
            self.lcd.move_to(0, 0)
            self.lcd.putstr(first_line)
        if second_line is not None:
            self.lcd.move_to(0, 1)
            self.lcd.putstr(second_line)

        time.sleep(duration)

    def timeout_callback(self) -> Optional["Page"]:
        self.display_temporary("Retour...")

    def encoder_callback(self, clockwise: bool) -> Optional["Page"]:
        pass

    def encoder_button_callback(self) -> Optional["Page"]:
        pass

    def red_button_callback(self) -> Optional["Page"]:
        print("Cancel ...")
        self.display_temporary("Cancel ...")
        return BasePage()

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        pass


class BasePage(Page):
    def __init__(self):
        super().__init__()

    @single_lcd_write
    def display(self):
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Bonjour !!")

    def encoder_callback(self, clockwise: bool) -> Optional["Page"]:
        return MenuPage()

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        return PersonPage(button_id)


class NameButtonPage(Page):
    values = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + [CUSTOM_CHARS_IDX["enter"]]

    def __init__(self):
        super().__init__()
        self.button_id = None
        self.name = ""
        self.encoder_idx = 0

    @single_lcd_write
    def display(self):
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
        value = self.values[self.encoder_idx]
        if (value == CUSTOM_CHARS_IDX["enter"]) and self.name:
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
    def __init__(self, button_id: int):
        super().__init__()
        self.button_id = button_id

    @single_lcd_write
    def display(self):
        with Database() as db:
            name = db.get_name(self.button_id)
            mugs = db.get_mugs(name)
        self.lcd.move_to(0, 0)
        self.lcd.putstr(f"Bonjour {name}!")
        self.lcd.move_to(0, 1)

        mugs_today = [
            mug for mug in mugs if mug["datetime"].date() == datetime.now().date()
        ]
        volume_today = sum(mug["value"] for mug in mugs_today)

        message = f"Ajd: {len(mugs_today)} tasses - {int(volume_today)} mL"
        self.lcd.scroll_message(message, row=1, sleep=0.2)

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        self.button_id = button_id


class MugPage(Page):
    def __init__(self, mug_value: Optional[float] = None):
        super().__init__()
        self.mug_value = mug_value
        self.person_ids = set()

    @single_lcd_write
    def display(self):
        if self.mug_value is None:
            # Pot is removed
            self.lcd.blink()

        else:
            self.lcd.move_to(0, 0)
            self.lcd.putstr(f"{int(self.mug_value)}mL - Pour ?")

            if self.person_ids:
                with Database() as db:
                    names = [db.get_name(person_id) for person_id in self.person_ids]
                message = " + ".join(names)
                self.lcd.scroll_message(message, row=1, sleep=0.1)

    def person_button_callback(self, button_id: int) -> Optional["Page"]:
        self.person_ids.add(str(button_id))

    def encoder_button_callback(self) -> Optional["Page"]:
        with Database() as db:
            for person_id in self.person_ids:
                db.add_mug(person_id, self.mug_value / len(self.person_ids))
        self.display_temporary("OK !")
        return BasePage()

    def timeout_callback(self) -> Optional["Page"]:
        if self.person_ids:
            self.encoder_button_callback()


class MenuPage(Page):
    PAGES = [
        dict(name="Nommer bouton", page=NameButtonPage()),
        dict(name="Voir les stats", page=None),
    ]

    def __init__(self):
        super().__init__()
        self.encoder_idx = 0

    @single_lcd_write
    def display(self):
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Menu...")
        self.lcd.move_to(0, 1)
        self.lcd.putstr(self.PAGES[self.encoder_idx]["name"])

    def encoder_callback(self, clockwise: bool) -> Optional["Page"]:
        increment = 1 if clockwise else -1
        self.encoder_idx = (self.encoder_idx + increment) % len(self.PAGES)

    def encoder_button_callback(self) -> Optional["Page"]:
        return self.PAGES[self.encoder_idx]["page"]
