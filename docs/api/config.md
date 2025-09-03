# Configuration API

Configuration options and settings for the coffee machine system.

## coffee.config

::: coffee.config

## Configuration Reference

### Hardware Pin Assignments

The coffee machine uses various GPIO pins and I2C addresses for hardware communication.

#### GPIO Pins

```python
# HX711 Scale Interface
HX711_DATA_PIN = 17      # Data pin for load cell amplifier
HX711_CLOCK_PIN = 27     # Clock pin for load cell amplifier

# Rotary Encoder
ENCODER_CLK_PIN = 23     # Encoder clock signal
ENCODER_DT_PIN = 24      # Encoder data signal  
ENCODER_SW_PIN = 25      # Encoder switch/button

# Control Buttons
RED_BUTTON_PIN = 22      # Emergency/cancel button
INTERRUPT_PIN = 4        # MCP23017 interrupt pin
```

#### I2C Addresses

```python
# I2C Device Addresses
LCD_I2C_ADDRESS = 0x27   # LCD display I2C address
MCP23017_ADDRESS = 0x20  # Button multiplexer address

# I2C Bus Configuration
I2C_BUS = 1              # I2C bus number (usually 1 on Pi)
I2C_SPEED = 100000       # I2C clock speed (100kHz)
```

### Weight Detection Parameters

Configuration for the scale and weight detection system.

```python
# Weight Thresholds
POT_WEIGHT_THRESHOLD = 80        # Minimum weight change to detect pot (grams)
MUG_WEIGHT_THRESHOLD = 20        # Minimum weight change to detect mug (grams)
STABILITY_THRESHOLD = 2.0        # Weight stability tolerance (grams)

# Scale Configuration
NUM_SCALE_READINGS = 5           # Number of readings to average
LEN_SCALE_BUFFER = 3            # Buffer size for stability analysis
SCALE_SAMPLE_RATE = 10          # Samples per second
REFERENCE_UNIT = 305.834        # Calibration reference unit

# Smoothing Parameters
SMOOTHING_WINDOW = 3            # Window size for moving average
SMOOTHING_METHOD = "median"     # "mean" or "median" filtering
```

### User Interface Settings

LCD display and interaction configuration.

```python
# LCD Display
LCD_WIDTH = 16              # Characters per row
LCD_HEIGHT = 2              # Number of rows
LCD_BACKLIGHT_TIMEOUT = 300 # Backlight timeout (seconds)

# Timeouts
PAGE_TIMEOUT = 15           # Page inactivity timeout (seconds)
BUTTON_DEBOUNCE_TIME = 0.05 # Button debounce period (seconds)
ENCODER_DEBOUNCE_TIME = 0.02 # Encoder debounce period (seconds)

# Animation Settings
SCROLL_SPEED = 0.5          # Text scroll speed (seconds per character)
BLINK_RATE = 1.0           # Cursor blink rate (Hz)
```

### Coffee Tracking Configuration

Settings for coffee consumption monitoring and user management.

```python
# User Assignment
MUG_BUTTON_LOOKBEHIND_DURATION = 15  # Seconds to look back for button presses
MAX_USERS = 16                       # Maximum number of users (buttons)
AUTO_ASSIGN_THRESHOLD = 300          # Auto-assign if only one user (seconds)

# Data Logging
DATABASE_PATH = "coffee_data.db"     # SQLite database file
LOG_RETENTION_DAYS = 90             # Days to keep consumption logs
BACKUP_INTERVAL_HOURS = 24          # Database backup interval

# Consumption Limits
DAILY_LIMIT_WARNING = 1000          # Daily consumption warning (grams)
HOURLY_LIMIT = 500                  # Hourly consumption limit (grams)
```

### Custom Display Characters

LCD custom character definitions for special symbols.

```python
# Custom Characters (8x8 pixel patterns)
CUSTOM_CHARS = {
    'enter': bytearray([0x10, 0x10, 0x10, 0x14, 0x12, 0x1F, 0x02, 0x04]),
    'coffee': bytearray([0x0E, 0x1F, 0x15, 0x1F, 0x17, 0x10, 0x10, 0x00]),
    'user': bytearray([0x0E, 0x11, 0x11, 0x0E, 0x04, 0x0A, 0x11, 0x00]),
    'weight': bytearray([0x00, 0x1F, 0x11, 0x11, 0x11, 0x1F, 0x04, 0x00]),
    'arrow_up': bytearray([0x04, 0x0E, 0x1F, 0x04, 0x04, 0x04, 0x04, 0x00]),
    'arrow_down': bytearray([0x04, 0x04, 0x04, 0x04, 0x1F, 0x0E, 0x04, 0x00])
}

# Character index mapping
CUSTOM_CHARS_IDX = {name: chr(idx) for idx, name in enumerate(CUSTOM_CHARS.keys())}
```

## Configuration Management

### Environment-Specific Settings

```python
import os
from typing import Optional

class Config:
    """Configuration management class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv('COFFEE_CONFIG', 'config.ini')
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or environment"""
        # Load from environment variables
        self.hx711_data_pin = int(os.getenv('HX711_DATA_PIN', '17'))
        self.hx711_clock_pin = int(os.getenv('HX711_CLOCK_PIN', '27'))
        self.lcd_address = int(os.getenv('LCD_I2C_ADDRESS', '0x27'), 16)
        self.pot_threshold = float(os.getenv('POT_WEIGHT_THRESHOLD', '80.0'))
        
        # Load from config file if it exists
        if os.path.exists(self.config_file):
            self.load_from_file()
    
    def load_from_file(self):
        """Load configuration from INI file"""
        import configparser
        config = configparser.ConfigParser()
        config.read(self.config_file)
        
        # Hardware section
        if 'hardware' in config:
            hw = config['hardware']
            self.hx711_data_pin = hw.getint('hx711_data_pin', self.hx711_data_pin)
            self.hx711_clock_pin = hw.getint('hx711_clock_pin', self.hx711_clock_pin)
            self.lcd_address = hw.getint('lcd_i2c_address', self.lcd_address)
        
        # Thresholds section
        if 'thresholds' in config:
            thresh = config['thresholds']
            self.pot_threshold = thresh.getfloat('pot_weight_threshold', self.pot_threshold)
    
    def save_config(self):
        """Save current configuration to file"""
        import configparser
        config = configparser.ConfigParser()
        
        config['hardware'] = {
            'hx711_data_pin': str(self.hx711_data_pin),
            'hx711_clock_pin': str(self.hx711_clock_pin),
            'lcd_i2c_address': f'0x{self.lcd_address:02x}'
        }
        
        config['thresholds'] = {
            'pot_weight_threshold': str(self.pot_threshold)
        }
        
        with open(self.config_file, 'w') as f:
            config.write(f)

# Global configuration instance
config = Config()
```

### Runtime Configuration Updates

```python
class RuntimeConfig:
    """Runtime configuration management"""
    
    def __init__(self):
        self.observers = []
        self.settings = {}
    
    def register_observer(self, callback):
        """Register callback for configuration changes"""
        self.observers.append(callback)
    
    def update_setting(self, key, value):
        """Update a configuration setting"""
        old_value = self.settings.get(key)
        self.settings[key] = value
        
        # Notify observers of change
        for callback in self.observers:
            callback(key, old_value, value)
    
    def get_setting(self, key, default=None):
        """Get a configuration setting"""
        return self.settings.get(key, default)

# Usage example
runtime_config = RuntimeConfig()

def on_config_change(key, old_value, new_value):
    print(f"Config changed: {key} = {new_value} (was {old_value})")

runtime_config.register_observer(on_config_change)
runtime_config.update_setting('pot_threshold', 90.0)
```

### Calibration Data Management

```python
import json
import os
from datetime import datetime

class CalibrationConfig:
    """Manage calibration data"""
    
    def __init__(self, calibration_file='calibration.json'):
        self.calibration_file = calibration_file
        self.data = self.load_calibration()
    
    def load_calibration(self):
        """Load calibration data from file"""
        if not os.path.exists(self.calibration_file):
            return self.get_default_calibration()
        
        try:
            with open(self.calibration_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self.get_default_calibration()
    
    def get_default_calibration(self):
        """Get default calibration values"""
        return {
            'scale': {
                'reference_unit': 305.834,
                'offset': 0,
                'last_calibrated': None
            },
            'thresholds': {
                'pot_weight': 80.0,
                'mug_weight': 20.0,
                'stability': 2.0
            }
        }
    
    def save_calibration(self):
        """Save calibration data to file"""
        with open(self.calibration_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def update_scale_calibration(self, reference_unit, offset):
        """Update scale calibration values"""
        self.data['scale']['reference_unit'] = reference_unit
        self.data['scale']['offset'] = offset
        self.data['scale']['last_calibrated'] = datetime.now().isoformat()
        self.save_calibration()
    
    def get_scale_calibration(self):
        """Get current scale calibration"""
        return self.data['scale']
    
    def update_threshold(self, threshold_type, value):
        """Update weight threshold"""
        if threshold_type in self.data['thresholds']:
            self.data['thresholds'][threshold_type] = value
            self.save_calibration()
```

### Hardware Profile Management

```python
class HardwareProfile:
    """Manage different hardware configurations"""
    
    PROFILES = {
        'raspberry_pi_4': {
            'gpio_pins': {
                'hx711_data': 17,
                'hx711_clock': 27,
                'encoder_clk': 23,
                'encoder_dt': 24,
                'encoder_sw': 25,
                'red_button': 22,
                'interrupt': 4
            },
            'i2c': {
                'bus': 1,
                'lcd_address': 0x27,
                'mcp23017_address': 0x20
            }
        },
        'raspberry_pi_zero': {
            'gpio_pins': {
                'hx711_data': 17,
                'hx711_clock': 27,
                'encoder_clk': 23,
                'encoder_dt': 24,
                'encoder_sw': 25,
                'red_button': 22,
                'interrupt': 4
            },
            'i2c': {
                'bus': 1,
                'lcd_address': 0x27,
                'mcp23017_address': 0x20
            }
        }
    }
    
    def __init__(self, profile_name='raspberry_pi_4'):
        self.profile_name = profile_name
        self.profile = self.PROFILES.get(profile_name, self.PROFILES['raspberry_pi_4'])
    
    def get_gpio_pin(self, pin_name):
        """Get GPIO pin number for a specific function"""
        return self.profile['gpio_pins'].get(pin_name)
    
    def get_i2c_address(self, device_name):
        """Get I2C address for a specific device"""
        return self.profile['i2c'].get(f'{device_name}_address')
    
    def get_i2c_bus(self):
        """Get I2C bus number"""
        return self.profile['i2c']['bus']

# Auto-detect hardware profile
def detect_hardware_profile():
    """Detect hardware profile based on system info"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
        
        if 'Pi 4' in model:
            return 'raspberry_pi_4'
        elif 'Pi Zero' in model:
            return 'raspberry_pi_zero'
        else:
            return 'raspberry_pi_4'  # Default
    except:
        return 'raspberry_pi_4'  # Default fallback
```

## Configuration Validation

```python
from typing import Dict, Any
import logging

class ConfigValidator:
    """Validate configuration values"""
    
    VALID_RANGES = {
        'pot_weight_threshold': (10.0, 1000.0),
        'num_scale_readings': (1, 20),
        'page_timeout': (5, 300),
        'hx711_data_pin': (0, 40),
        'hx711_clock_pin': (0, 40),
        'lcd_i2c_address': (0x08, 0x77)
    }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> bool:
        """Validate configuration dictionary"""
        valid = True
        
        for key, value in config.items():
            if not cls.validate_setting(key, value):
                valid = False
        
        return valid
    
    @classmethod
    def validate_setting(cls, key: str, value: Any) -> bool:
        """Validate a single configuration setting"""
        if key not in cls.VALID_RANGES:
            logging.warning(f"Unknown configuration key: {key}")
            return True  # Allow unknown keys
        
        min_val, max_val = cls.VALID_RANGES[key]
        
        try:
            num_value = float(value)
            if not (min_val <= num_value <= max_val):
                logging.error(f"Invalid value for {key}: {value} (must be between {min_val} and {max_val})")
                return False
        except (ValueError, TypeError):
            logging.error(f"Invalid type for {key}: {value} (must be numeric)")
            return False
        
        return True
    
    @classmethod
    def sanitize_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize configuration values to valid ranges"""
        sanitized = {}
        
        for key, value in config.items():
            if key in cls.VALID_RANGES:
                min_val, max_val = cls.VALID_RANGES[key]
                try:
                    num_value = float(value)
                    sanitized[key] = max(min_val, min(max_val, num_value))
                except (ValueError, TypeError):
                    # Use default value for invalid types
                    sanitized[key] = (min_val + max_val) / 2
            else:
                sanitized[key] = value
        
        return sanitized
```

For the complete configuration module implementation, see the source code using the `:::` directive above.