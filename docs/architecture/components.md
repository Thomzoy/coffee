# Components

Detailed documentation for each system component, including their responsibilities, interfaces, and implementation details.

## IO Layer Components

### Scale Module (`coffee.io.scale`)

The scale module provides weight measurement functionality using HX711 load cell amplifiers.

#### Key Classes

**Scale**
- Manages HX711 hardware interface
- Implements noise filtering and data smoothing
- Provides thread-safe weight readings
- Handles calibration and offset management

#### Key Features

- **Continuous Reading:** Background thread for constant weight monitoring
- **Data Filtering:** Median filtering to reduce noise
- **Event Detection:** Automatic pot removal/return detection
- **Calibration Support:** Weight calibration and offset adjustment

#### Configuration

```python
# Key parameters in coffee/config.py
POT_WEIGHT_THRESHOLD = 80      # Detection threshold (grams)
NUM_SCALE_READINGS = 5         # Readings per measurement
LEN_SCALE_BUFFER = 3          # Buffer size for stability
```

#### Usage Example

```python
from coffee.io.scale import Scale

scale = Scale()
scale.start_reading()

# Get latest reading
weight = scale.get_latest_reading()
print(f"Current weight: {weight}g")

# Monitor for changes
while True:
    if scale.has_pot_changed():
        print("Pot status changed!")
```

### LCD Module (`coffee.io.lcd`)

Manages the 16x2 I2C LCD display with thread-safe operations and custom character support.

#### Key Classes

**LCD**
- Extends `I2cLcd` with additional functionality
- Implements thread-safe display operations
- Supports custom characters and scrolling text
- Manages backlight and cursor control

#### Key Features

- **Thread Safety:** Decorator-based locking for concurrent access
- **Custom Characters:** Support for special symbols (enter, progress bars)
- **Text Scrolling:** Animated text scrolling for long messages
- **Smart Updates:** Prevents display corruption during updates

#### Display Operations

```python
from coffee.io.lcd import LCD

lcd = LCD()

# Basic display
lcd.clear()
lcd.move_to(0, 0)
lcd.putstr("Hello World!")

# Thread-safe scrolling
lcd.scroll_message("This is a long message that will scroll", row=1)

# Custom characters
lcd.putchar(chr(0))  # Display custom character
```

### Multiplex Module (`coffee.io.multiplex`)

Interfaces with MCP23017 I2C GPIO expander for button matrix management.

#### Key Classes

**Multiplex**
- Manages 16-button matrix via MCP23017
- Implements interrupt-driven button detection
- Provides debouncing and event filtering
- Handles pull-up resistor configuration

#### Button Mapping

```python
# Button layout (0-15)
BUTTON_LAYOUT = [
    [0,  1,  2,  3 ],   # Row 1: Person buttons 0-3
    [4,  5,  6,  7 ],   # Row 2: Person buttons 4-7  
    [8,  9,  10, 11],   # Row 3: Person buttons 8-11
    [12, 13, 14, 15]    # Row 4: Person buttons 12-15
]
```

#### Interrupt Handling

```python
def setup_button_interrupts(app):
    """Configure button interrupt handling"""
    def interrupt_callback():
        flags_a, flags_b = mcp.read_interrupt_capture()
        button_id = decode_button_press(flags_a, flags_b)
        app.person_button_callback(button_id)
    
    button_pin.when_pressed = interrupt_callback
```

### Encoder Module (`coffee.io.encoder`)

Handles rotary encoder input with button press detection.

#### Key Classes

**Encoder**
- Manages rotary encoder GPIO interface
- Implements rotation direction detection
- Provides button press/release events
- Includes debouncing logic

#### Encoder Events

```python
from coffee.io.encoder import Encoder

encoder = Encoder(clk_pin=23, dt_pin=24, sw_pin=25)

def handle_rotation(direction):
    if direction > 0:
        print("Clockwise rotation")
    else:
        print("Counter-clockwise rotation")

def handle_button():
    print("Button pressed")

encoder.when_rotated = handle_rotation
encoder.when_pressed = handle_button
```

## Application Layer Components

### LCDApp (`coffee.app.app`)

The main application controller that coordinates all system components.

#### Key Responsibilities

- **Component Integration:** Brings together all IO modules
- **Event Orchestration:** Routes hardware events to appropriate handlers
- **Page Management:** Controls UI state transitions
- **Timeout Handling:** Manages inactivity timeouts

#### Core Architecture

```python
class LCDApp:
    def __init__(self):
        self.lcd = LCD()
        self.scale = Scale()
        self.multiplex = Multiplex()
        self.encoder = Encoder()
        self.page = BasePage()
        
    def setup_callbacks(self):
        """Register hardware event callbacks"""
        self.encoder.when_rotated = self.encoder_callback
        self.encoder.when_pressed = self.encoder_button_callback
        # ... other callbacks
```

#### Event Callbacks

All callbacks use the `@set_page` decorator for automatic page transitions:

```python
@set_page
def encoder_callback(self, clockwise: bool):
    """Handle encoder rotation"""
    return self.page.encoder_callback(clockwise)

@set_page
def person_button_callback(self, button_id):
    """Handle person button press"""
    return self.page.person_button_callback(button_id)
```

### Page System (`coffee.app.page`)

Implements the UI state machine using the State pattern.

#### Base Page Class

**Page**
- Defines the interface for all pages
- Provides default implementations for callbacks
- Manages LCD display operations
- Handles timeout behavior

#### Page Types

**BasePage**
- Default home screen
- Shows welcome message
- Entry point for navigation

**MenuPage**
- Settings and configuration menu
- Encoder-driven navigation
- Access to sub-features

**PersonPage**
- Displays individual user information
- Shows coffee consumption stats
- Accessed via person buttons

**MugPage**
- Coffee serving confirmation
- User assignment interface
- Automatic after coffee detection

**NameButtonPage**
- Button naming interface
- Character selection via encoder
- Name assignment workflow

#### Page Transitions

```python
def encoder_callback(self, clockwise: bool):
    """Example page transition"""
    if clockwise:
        return MenuPage()  # Transition to menu
    else:
        return self  # Stay on current page
```

### Database Module (`coffee.app.db`)

Manages data persistence using SQLite.

#### Key Classes

**Database**
- SQLite database interface
- Coffee consumption logging
- User preference storage
- Data query and reporting

#### Database Schema

```sql
-- Coffee consumption logs
CREATE TABLE coffee_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    timestamp DATETIME,
    amount_grams REAL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- User information
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    button_id INTEGER UNIQUE
);
```

#### Usage Examples

```python
from coffee.app.db import Database

db = Database()

# Log coffee consumption
db.log_coffee(user_id=1, amount=250.5)

# Get user stats
stats = db.get_user_stats(user_id=1)
print(f"Total coffee: {stats['total_amount']}g")
```

## Configuration Component

### Config Module (`coffee.config`)

Centralized configuration management for the entire system.

#### Hardware Configuration

```python
# GPIO pin assignments
ENCODER_CLK_PIN = 23
ENCODER_DT_PIN = 24
ENCODER_SW_PIN = 25
RED_BUTTON_PIN = 22

# I2C addresses
LCD_I2C_ADDRESS = 0x27
MCP23017_ADDRESS = 0x20

# HX711 pins
HX711_DATA_PIN = 17
HX711_CLOCK_PIN = 27
```

#### Operational Parameters

```python
# Weight detection
POT_WEIGHT_THRESHOLD = 80       # grams
NUM_SCALE_READINGS = 5          # readings per measurement
LEN_SCALE_BUFFER = 3           # stability buffer size

# User interface
LCD_TIMEOUT = 15               # seconds
BUTTON_DEBOUNCE_TIME = 0.1     # seconds
SCROLL_SPEED = 0.5             # seconds per character

# Coffee tracking
MUG_BUTTON_LOOKBEHIND_DURATION = 15  # seconds
```

#### Custom Characters

```python
# LCD custom character definitions
CUSTOM_CHARS = {
    'enter': bytearray([0x10, 0x10, 0x10, 0x14, 0x12, 0x1F, 0x02, 0x04])
}
```

## Component Interactions

### Startup Sequence

1. **Configuration Loading:** Read settings from `config.py`
2. **Hardware Initialization:** Initialize all IO components
3. **Callback Registration:** Set up event handlers
4. **Page Display:** Show initial BasePage
5. **Background Tasks:** Start scale reading thread

### Event Flow

1. **Hardware Event:** Button press, encoder rotation, weight change
2. **Interrupt/Polling:** Hardware detection mechanism
3. **Callback Invocation:** Appropriate app callback called
4. **Page Processing:** Current page handles the event
5. **Page Transition:** New page returned (if applicable)
6. **Display Update:** LCD shows new page content

### Data Flow

1. **Sensor Reading:** Continuous scale measurements
2. **Data Processing:** Filtering and smoothing
3. **Event Detection:** Weight pattern analysis
4. **User Interaction:** Button/encoder input
5. **Data Logging:** Database storage
6. **Display Feedback:** LCD confirmation

## Error Handling

### Hardware Errors

- **I2C Communication Failures:** Retry with exponential backoff
- **GPIO Access Errors:** Graceful degradation
- **Sensor Disconnection:** Clear error messages

### Software Errors

- **Page Exceptions:** Return to BasePage
- **Database Errors:** Log and continue
- **Threading Issues:** Proper cleanup and recovery

## Performance Optimizations

### Memory Management

- Circular buffers for sensor data
- Limited object creation in loops
- Efficient string operations

### CPU Optimization

- Non-blocking I/O operations
- Optimized sensor reading frequency
- Minimal LCD update calls

### Thread Coordination

- Lock-free data structures where possible
- Efficient inter-thread communication
- Proper thread lifecycle management

## Testing and Debugging

### Hardware Testing

```python
# Test individual components
def test_scale():
    scale = Scale()
    for i in range(10):
        print(f"Reading {i}: {scale.read_sensor_value()}g")

def test_lcd():
    lcd = LCD()
    lcd.clear()
    lcd.putstr("Test message")
```

### Debug Output

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Component-specific debug flags
DEBUG_SCALE = True
DEBUG_BUTTONS = True
DEBUG_DISPLAY = True
```

## Extension Points

### Adding New Hardware

1. Create new module in `coffee.io`
2. Implement standard interface
3. Add configuration parameters
4. Register callbacks in LCDApp

### Custom Pages

1. Inherit from `Page` base class
2. Implement required callbacks
3. Add to navigation flow
4. Update menu system

### New Features

1. Extend database schema
2. Add configuration options
3. Create supporting pages
4. Update documentation

For implementation details, see the [API Reference](../api/app.md).