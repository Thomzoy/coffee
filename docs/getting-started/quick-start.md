# Quick Start

Get your coffee machine up and running quickly with this step-by-step guide.

## Prerequisites

Before starting, ensure you have:

- [x] Completed the [installation](installation.md)
- [x] Finished [hardware setup](hardware-setup.md)
- [x] All components are connected and powered

## First Run

### 1. Test Hardware Connections

Verify your hardware is working:

```bash
# Check I2C devices
i2cdetect -y 1

# Should show:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 20: 20 -- -- -- -- -- -- 27 -- -- -- -- -- -- -- -- 
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

### 2. Run the Main Application

Start the coffee machine interface:

```bash
cd /path/to/coffee
python scripts/main.py
```

You should see:
- LCD display lights up showing "Bonjour !!"
- Weight readings begin in the console
- System responds to button presses and encoder rotation

### 3. Basic Operation Test

Test the core functionality:

=== "Weight Detection"

    1. **Place an empty coffee pot** on the scale
    2. **Observe the weight reading** stabilize
    3. **Remove the pot** - system should detect removal
    4. **Return the pot** - system should detect return

=== "User Interface"

    1. **Turn the rotary encoder** - should navigate to menu
    2. **Press encoder button** - should select menu item
    3. **Press red button** - should return to home screen
    4. **Press any person button** - should show person page

=== "Coffee Serving Simulation"

    1. **Remove coffee pot** from scale
    2. **Add weight to simulate mug** (place something on scale)
    3. **System should detect serving** and ask who drank coffee
    4. **Press a person button** to assign the coffee

## Configuration

### Scale Calibration

For accurate measurements, calibrate the scale:

```bash
# Run calibration script
python scripts/calibrate.py
```

Follow the on-screen instructions:
1. Remove all weight from scale
2. Place a known weight (e.g., 1kg)
3. Enter the actual weight value
4. Save the calibration

### User Button Setup

Assign names to person buttons:

1. **From home screen**, turn encoder to navigate to "Nommer bouton"
2. **Press encoder** to enter naming mode
3. **Press the button** you want to name
4. **Use encoder to scroll** through letters A-Z
5. **Press encoder** to select each letter
6. **Navigate to ↵ symbol** and press encoder to finish

## Understanding the Interface

### Display Pages

The system has several interface pages:

| Page | Description | Navigation |
|------|-------------|------------|
| **Home (Bonjour !!)** | Default display | Base page |
| **Menu** | Settings and options | Turn encoder from home |
| **Person Page** | Shows user info | Press person button |
| **Mug Page** | Coffee serving confirmation | Automatic after serving |
| **Name Button** | Assign button names | From menu |

### Status Indicators

Watch for these indicators:

- **Backlight blinking:** System processing
- **Text scrolling:** Long messages
- **Temporary messages:** Confirmations and errors

## Common First-Run Issues

### Scale Issues

**Problem:** Erratic weight readings
```bash
# Check connections
# Verify HX711 wiring
# Run: python -c "from coffee.io.scale import Scale; s=Scale(); print(s.read_sensor_value())"
```

**Problem:** No weight readings
```bash
# Check HX711 power (5V)
# Verify GPIO pins 17, 27
# Check load cell connections
```

### LCD Issues

**Problem:** LCD shows garbage or nothing
```bash
# Power cycle LCD module
# Check I2C address: i2cdetect -y 1
# Verify 5V power to LCD
```

**Problem:** LCD backlight but no text
```bash
# Check I2C communication
# Try different I2C address in config
# Restart application
```

### Button Issues

**Problem:** Buttons not responding
```bash
# Check MCP23017 on I2C bus
# Verify interrupt pin connection (GPIO 4)
# Test button connections to ground
```

**Problem:** Encoder not working
```bash
# Check encoder pins (GPIO 23, 24, 25)
# Verify 3.3V power
# Test rotation and button press separately
```

## Monitoring and Logs

### Console Output

The application provides detailed console output:

```
Encoder - Clockwise True - Page BasePage
Person button callback - ID 0 - Page BasePage  
New mug - 245.3 g
[INFO] POLLING_BASED | longValue: 12450 | weight (grams): 245.3
```

### Log Levels

For debugging, increase verbosity:

```python
# In scripts/main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing Coffee Workflow

Simulate a complete coffee workflow:

1. **Start with empty scale** - weight should be ~0g
2. **Place coffee pot** - weight increases significantly  
3. **Remove pot** - weight drops, system detects removal
4. **Place empty mug** - small weight increase
5. **Add liquid to mug** - weight increase simulates served coffee
6. **System prompts** for user assignment
7. **Press person button** - coffee is logged to that user

## Data Storage

Coffee consumption data is stored in:
```
scripts/app_data.db
```

View the data:
```bash
sqlite3 scripts/app_data.db
.tables
SELECT * FROM coffee_logs;
```

## Next Steps

Now that your system is running:

1. **[Learn the interface](../user-guide/interface.md)** - Master all features
2. **[Calibrate properly](../user-guide/calibration.md)** - Ensure accuracy  
3. **[Set up systemd service](installation.md#systemd-service-optional)** - Auto-start on boot
4. **[Explore the architecture](../architecture/overview.md)** - Understand the system

## Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](../user-guide/troubleshooting.md)
2. Review console output for error messages
3. Verify hardware connections
4. Open an issue on [GitHub](https://github.com/Thomzoy/coffee/issues)

Enjoy your smart coffee machine! ☕