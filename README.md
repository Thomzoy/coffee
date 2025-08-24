# Python

* gpiozero
* mcp23017
* hx711_gpiozero
* https://github.com/dhylands/python_lcd

# Misc

* sudo apt install python3-smbus

# GPIO daemon

Daemon that runs as root in the background, so that non-root user can access GPIO:

```
sudo apt update
sudo apt install pigpio python3-pigpio
sudo systemctl start pigpiod
sudo systemctl enable pigpiod  # Enable on boot
```

# Scale
https://github.com/endail/hx711 and https://pypi.org/project/hx711-rpi-py/
* sudo apt-get install -y liblgpio-dev