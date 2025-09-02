# Installation

This guide will help you install and set up the coffee machine software on your Raspberry Pi.

## Prerequisites

- Raspberry Pi (tested on Pi 4) running DietPI or Raspberry Pi OS
- Python 3.8 or higher
- Git
- Internet connection for downloading dependencies

## System Dependencies

### I2C Support

Enable I2C and install the necessary packages:

```bash
# Enable I2C (if not already enabled)
sudo raspi-config  # Navigate to Interface Options > I2C > Enable

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

### Method 1: Development Installation (Recommended)

Clone the repository and install in development mode:

```bash
# Clone the repository
git clone https://github.com/Thomzoy/coffee.git
cd coffee

# Install in development mode with documentation dependencies
pip install -e ".[docs]"
```

### Method 2: Direct Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/Thomzoy/coffee.git
```

## Hardware Setup

Before running the software, ensure your hardware is properly connected. See the [Hardware Setup Guide](hardware-setup.md) for detailed wiring instructions.

## Verification

Verify your installation by running the test script:

```bash
cd coffee/scripts
python main.py
```

If everything is configured correctly, you should see the LCD display initialize and weight readings begin.

## Documentation (Optional)

To build and serve the documentation locally:

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Serve documentation locally
mkdocs serve
```

The documentation will be available at `http://localhost:8000`.

## Systemd Service (Optional)

To run the coffee machine automatically on boot:

```bash
# Copy the systemd service file
sudo cp scripts/systemd/coffee.service /etc/systemd/system/

# Enable and start the service
sudo systemctl enable coffee.service
sudo systemctl start coffee.service

# Check status
sudo systemctl status coffee.service
```

## Troubleshooting

### Common Issues

**Permission Denied on GPIO**
```bash
# Ensure pigpiod is running
sudo systemctl status pigpiod
sudo systemctl start pigpiod
```

**I2C Device Not Found**
```bash
# Check I2C devices
i2cdetect -y 1

# Enable I2C if not already enabled
sudo raspi-config
```

**ImportError for hx711-rpi-py**
```bash
# Ensure C++ dependencies are installed
sudo apt-get install -y liblgpio-dev
# Reinstall the package
pip uninstall hx711-rpi-py
pip install hx711-rpi-py
```

**LCD Display Not Working**
- Check I2C connections and address (default: 0x27)
- Verify the LCD has power
- Try power cycling the LCD module

For more troubleshooting help, see the [Troubleshooting Guide](../user-guide/troubleshooting.md).

## Next Steps

Once installation is complete:

1. [Set up your hardware](hardware-setup.md) - Wire the components
2. [Quick start guide](quick-start.md) - Get your first coffee reading
3. [Calibrate the scale](../user-guide/calibration.md) - Ensure accurate measurements