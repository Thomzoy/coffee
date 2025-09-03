# Installation

This guide will help you install and set up the coffee machine software on your Raspberry Pi.

## Prerequisites

- Raspberry Pi running DietPI
- Python 3.8 or higher
- Git

## System Dependencies

### I2C Support

Enable I2C and install the necessary packages:

```bash
# Enable I2C (if not already enabled)
sudo dietpi-config  # Navigate to Interface Options > I2C > Enable

# Install I2C Python support
sudo apt update
sudo apt install python3-smbus
```

### GPIO Daemon

Install and configure the GPIO daemon for proper GPIO access:

```bash
sudo apt update
sudo apt install pigpio python3-pigpio

# Start the daemon
sudo systemctl start pigpiod

# Enable on boot
sudo systemctl enable pigpiod
```

### HX711 C++ Library

The scale interface requires the HX711 C++ library:

```bash
# Install dependencies
sudo apt-get install -y liblgpio-dev

# Clone and build the HX711 library
git clone https://github.com/endail/hx711
cd hx711
make
sudo make install
sudo ldconfig
cd ..
```

## Python Package Installation

Clone the repository and install in development mode:

```bash
git clone https://github.com/Thomzoy/coffee.git
cd coffee
pip install -e ".[docs]"
```

## Hardware Setup

Before running the software, ensure your hardware is properly connected.

## Run

```bash
cd coffee/scripts
python main.py
```

!!! warning
     Be sure to run only one script at a time to avoid garbage weight reading and/or LCD display. Notably be sure to stop the service 
     via `sudo systemctl stop coffee.service` before running the script manualy

If everything is configured correctly, you should see the LCD display initialize and weight readings begin.

## Systemd Service

To run the coffee machine automatically on boot:

```bash
# Copy the systemd service file
sudo cp scripts/systemd/coffee.service /etc/systemd/system/

# Enable and start the service
sudo systemctl enable coffee.service
sudo systemctl start coffee.service

# Check status
sudo systemctl status coffee.service

# Check logs
sudo journalctl -u coffee.service
```
