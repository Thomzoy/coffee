# Hardware Setup

This guide covers the physical setup and wiring of the coffee machine components.

## Required Hardware

### Core Components

- **Raspberry Pi 4** (or compatible)
- **HX711 Load Cell Amplifier** - For weight sensing
- **4x Load Cells** - Weight sensors (arranged under coffee machine platform)
- **16x2 LCD Display with I2C Backpack** - User interface
- **Rotary Encoder with Button** - Navigation control
- **MCP23017 I2C GPIO Expander** - Button multiplexing
- **16 Push Buttons** - User input (person buttons + red button)

### Additional Components

- Breadboard or PCB for connections
- Jumper wires and connectors
- Pull-up resistors (if not using internal pull-ups)
- 5V power supply (Pi can provide 3.3V for most components)

## Wiring Diagrams

### I2C Bus Connections

All I2C devices share the same bus:

| Component | SDA Pin | SCL Pin | Address |
|-----------|---------|---------|---------|
| LCD Display | GPIO 2 (SDA) | GPIO 3 (SCL) | 0x27 |
| MCP23017 | GPIO 2 (SDA) | GPIO 3 (SCL) | 0x20 |

### HX711 Scale Connection

The HX711 connects directly to GPIO pins:

| HX711 Pin | Raspberry Pi Pin | GPIO |
|-----------|------------------|------|
| VCC | 5V | - |
| GND | Ground | - |
| DT (Data) | Pin 11 | GPIO 17 |
| SCK (Clock) | Pin 13 | GPIO 27 |

### Rotary Encoder

| Encoder Pin | Raspberry Pi Pin | GPIO |
|-------------|------------------|------|
| CLK | Pin 16 | GPIO 23 |
| DT | Pin 18 | GPIO 24 |
| SW (Button) | Pin 22 | GPIO 25 |
| VCC | 3.3V | - |
| GND | Ground | - |

### Red Button

| Button Pin | Raspberry Pi Pin | GPIO |
|------------|------------------|------|
| Signal | Pin 15 | GPIO 22 |
| Ground | Ground | - |

*Note: Use internal pull-up resistor in software*

### MCP23017 Button Connections

Connect the 16 person buttons to the MCP23017 GPIO pins:

**Bank A (GPA0-GPA7):**
- Buttons 0-7

**Bank B (GPB0-GPB7):**  
- Buttons 8-15

All buttons should be wired with one side to ground and the other to the respective GPIO pin. The MCP23017 is configured with internal pull-up resistors.

### Interrupt Pin

Connect the MCP23017 interrupt pin to the Raspberry Pi:

| MCP23017 Pin | Raspberry Pi Pin | GPIO |
|--------------|------------------|------|
| INTA | Pin 7 | GPIO 4 |

## Load Cell Platform Setup

### Physical Arrangement

Arrange the 4 load cells in a rectangular configuration under your coffee machine platform:

```
[Load Cell 1] ---- [Load Cell 2]
      |                  |
      |    Platform      |
      |                  |
[Load Cell 4] ---- [Load Cell 3]
```

### Load Cell Wiring

Connect all load cells to the HX711 in a Wheatstone bridge configuration:

- **E+ (Excitation+):** Red wires from all load cells
- **E- (Excitation-):** Black wires from all load cells  
- **A+ (Signal+):** White wires from load cells 1&2, Green wires from 3&4
- **A- (Signal-):** Green wires from load cells 1&2, White wires from 3&4

!!! warning "Load Cell Calibration"
    Load cells must be calibrated after installation. See the [Calibration Guide](../user-guide/calibration.md) for detailed instructions.

## LCD Display Setup

### I2C Address Configuration

Most LCD I2C backpacks use address `0x27`. To verify your LCD address:

```bash
i2cdetect -y 1
```

If your LCD uses a different address, update the configuration in `coffee/config.py`.

### Custom Characters

The LCD is configured to display custom characters for the user interface:

- **Enter symbol (↵):** Used in name input mode
- **Progress indicators:** For various UI states

## Power Considerations

### Power Requirements

- **Raspberry Pi:** 5V, 3A recommended
- **LCD Display:** 5V (via I2C backpack) 
- **Load Cells:** 5V excitation (via HX711)
- **Buttons/Encoder:** 3.3V logic

### Power Distribution

The Raspberry Pi can power most components through its GPIO pins:

- Use 5V pins for HX711 and LCD
- Use 3.3V pins for logic signals
- Ensure adequate current capacity for all components

## Testing Hardware Connections

### I2C Device Detection

Verify I2C devices are detected:

```bash
i2cdetect -y 1
```

Expected output should show devices at:
- `0x20` - MCP23017
- `0x27` - LCD Display (may vary)

### GPIO Testing

Test individual components:

```bash
# Test rotary encoder
python3 -c "
import gpiozero
encoder = gpiozero.RotaryEncoder(23, 24)
print('Turn encoder - should see value changes')
while True: print(encoder.value)
"

# Test scale readings
cd coffee/scripts
python3 -c "
from coffee.io.scale import Scale
scale = Scale()
scale.start_reading()
print('Place weight on scale - should see readings')
while True: print(scale.get_latest_reading())
"
```

## Troubleshooting Hardware

### Common Issues

**No I2C Devices Detected:**
- Check SDA/SCL connections
- Verify I2C is enabled: `sudo raspi-config`
- Check pull-up resistors (usually built into I2C devices)

**Scale Readings are Unstable:**
- Check HX711 connections
- Ensure load cells are properly mounted
- Verify platform is stable and level
- Check for electrical interference

**Buttons Not Responding:**
- Verify MCP23017 connections
- Check interrupt pin connection
- Test with multimeter for proper ground connections

**LCD Shows Garbage Characters:**
- Power cycle the LCD module
- Check I2C address is correct
- Verify 5V power supply to LCD

### Advanced Troubleshooting

For more detailed troubleshooting, see the [Troubleshooting Guide](../user-guide/troubleshooting.md).

## Next Steps

After completing the hardware setup:

1. [Run the quick start guide](quick-start.md) to test your setup
2. [Calibrate the scale](../user-guide/calibration.md) for accurate measurements
3. [Configure user buttons](../user-guide/interface.md) for your users