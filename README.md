# Coffee Machine Interface

A Raspberry Pi-based coffee machine interface with weight sensing, LCD display, and user tracking.

## Documentation

📖 **[Full Documentation](https://thomzoy.github.io/coffee)** - Complete setup, usage, and API reference

## Quick Start

For detailed instructions, see the [Getting Started Guide](https://thomzoy.github.io/coffee/getting-started/installation/).

### Installation

```bash
git clone https://github.com/Thomzoy/coffee.git
cd coffee
pip install -e ".[docs]"
```

### Local Documentation

To build and serve the documentation locally:

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs serve
```

Then visit `http://localhost:8000` to view the documentation.

## How to use

* Take the pot and serve coffee to one or more mugs.
* When you put the pot back, the volume of served coffee is displayed, and the app asks who got the coffee.
    * If some person buttons were pressed a short time **before** the coffee was served, those persons are displayed. 
    * You can also add person bypressing buttons after the serving
    * In any case, if there is a mistake, you can press the red button to remove the last displayed person

**To set the name corresponding to a button**
* From the home page, scroll the rotary encoder until page "Nommer bouton". THen click
* Press the button you want to name
* To write the name, scroll through the letters, and press the rotary encoder to select a letter
* When done, scroll to the special *enter* character ↵ located after "Z" and press the encoder

# Requirements

The PI runs DietPI, which has a lot on configuration option available via `dietpi-config`

## I2C

`sudo apt install python3-smbus`

## GPIO daemon

Daemon that runs as root in the background, so that non-root user can access GPIO:

```
sudo apt update
sudo apt install pigpio python3-pigpio
sudo systemctl start pigpiod
sudo systemctl enable pigpiod  # Enable on boot
```

## HX711 c++ library

We're using https://github.com/endail/hx711-rpi-py. It has c++ dependencies, check how to install here https://github.com/endail/hx711-rpi-py/blob/master/src/install-deps.sh or below:

```bash
apt-get install -y liblgpio-dev;
git clone https://github.com/endail/hx711;
cd hx711;
make;
make install;
ldconfig;
cd ..;
```


## Run on boot (already done)
See coffee/scripts/systemd

# How it works
## Inputs
### Scale: coffee.io.scale.scale.Scale
* The scale works with 4 load cell and a HX711 amplifier
* HX711 works by providing a clock signal and reading a data pin
* Readings should be aggregated as some outliers can exist
* A separate thread handles the continuous reading of weight

### Buttons: coffee.io.multiplex.Multiplex
* All 16 buttons are plugged into a MCP23017 multiplexer, which continuously saves the state of the buttons into a 16 bits registry
* This multiplexer then connects to the Pi via I2C
* An *interrupt* pin is also connected to the Pi: its value is set to high when one of the button is pressed. /!\ Once this interrupt was triggered, the registry should be read to reset it.

### Rotary encoder: coffee.io.encoder.Encoder
* The rotary encoder allows some user input. It can also be clicked.
* It works by providing a clock signal and reading a data pin
* The red button next to it acts as a *back/cancel* button

## LCD: coffee.io.lcd.LCD
* LCD screen connected to the Pi via I2C
* /!\ only one thread should write to it at a time, or it might start displaying garbage (if so, restart is necessary)

## Technical Workflow
* A thread continuously reads the weight from the scale
* An app (coffee.app.app.LcdApp) runs and displays a Page (coffee.app.page.Page) on the LCD display
* The app has some callbacks that are called when a specific event occurs:
    * `encoder_callback(self, clockwise: bool)`: when the rotary encoder is turned
    * `encoder_button_callback(self)`: when the rotary encoder button is pressed
    * `red_button_callback(self)`: when the red button is pressed
    * `person_button_callback(self, button_id)`: when a person button is pressed
    * `removed_pot_callback(self)`: when the coffee pot was removed (drop of weight)
    * `served_mug_callback(self, mug_value: float)`: when a mug was served (i.e., the scale detected a weight increase after the pot was removed). `mug_value` holds the weight (gr) of the mug
* Each page can re-define those callbacks to do different things.
* Those callbacks can return a Page (for instance, to change page when an event occurs). If something else is returned, the current Page's `display` method is simply run
* By default, a timeout of 15 seconds exists: if nothing happens during this time, the App goes back to the home page
* Some configuration is avaiable under `coffee/config.py`

## The different pages
See `coffee/app/pages.py` for descriptions and definitions

* `BasePage`: Default home page, nothing special
* `PersonPage`: Displayed when a person button is pressed from the BasePage, and displays some infos
* `MugPage`: Displayed when 1. the coffee pot is removed and 2. the coffee mug is put back. 
* `MenuPage`: Displayed when turning the rotary encoder from the `BasePage`. Can show various other pages, for the moment only 1:
    * `NameButtonPage`: Is used to assign a name to a button

## Misc
* Careful when writing to the LCD: it can glitch if e.g. a command is interrupted during sending (which can be frequent if using threads), so be sure to check if something is writing before writing. If it glitches, you should 1) try to turn it off and on (small switch behind the board) or 2) turn off the Pi THEN unplug it, wait a bit and replug it.