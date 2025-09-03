# IO Module API

API documentation for the input/output hardware interface modules.

## coffee.io.scale

::: coffee.io.scale

## coffee.io.lcd

::: coffee.io.lcd

## coffee.io.multiplex

::: coffee.io.multiplex

## coffee.io.encoder

::: coffee.io.encoder

## Usage Examples

### Scale Operations

```python
from coffee.io.scale import Scale
import time

# Initialize scale with custom parameters
scale = Scale(
    data_pin=17,
    clock_pin=27,
    reference_unit=305.834,  # Calibration value
    smoothing_window=5       # Number of readings to average
)

# Start continuous reading in background thread
scale.start_reading()

# Wait for scale to stabilize
time.sleep(2)

# Get current weight
current_weight = scale.get_latest_reading()
print(f"Current weight: {current_weight:.1f}g")

# Monitor for weight changes
previous_weight = current_weight
while True:
    weight = scale.get_latest_reading()
    if abs(weight - previous_weight) > 10:  # 10g threshold
        print(f"Weight change detected: {weight:.1f}g")
        previous_weight = weight
    time.sleep(0.1)

# Stop reading when done
scale.stop_reading()
```

### LCD Display Operations

```python
from coffee.io.lcd import LCD
import time

# Initialize LCD with custom I2C address
lcd = LCD(i2c_addr=0x27, num_lines=2, num_columns=16)

# Basic text display
lcd.clear()
lcd.move_to(0, 0)
lcd.putstr("Coffee Machine")
lcd.move_to(0, 1)
lcd.putstr("Ready!")

# Scrolling text for long messages
lcd.scroll_message("This is a very long message that will scroll across the display", row=1)

# Custom characters
lcd.custom_char(0, bytearray([0x0E, 0x1F, 0x15, 0x1F, 0x17, 0x10, 0x10, 0x00]))  # Coffee cup
lcd.move_to(15, 0)
lcd.putchar(chr(0))  # Display custom character

# Backlight control
lcd.backlight_off()
time.sleep(1)
lcd.backlight_on()

# Cursor control
lcd.show_cursor()
lcd.blink_cursor_on()
lcd.move_to(8, 1)
```

### Button Matrix Operations

```python
from coffee.io.multiplex import Multiplex
import time

# Initialize MCP23017 multiplexer
mcp = Multiplex(i2c_addr=0x20)

# Configure all pins as inputs with pull-ups
mcp.set_all_input()
mcp.enable_pullups()

# Set up interrupt detection
mcp.setup_interrupts()

# Read button states
def check_buttons():
    """Check current state of all buttons"""
    port_a = mcp.read_port_a()
    port_b = mcp.read_port_b()
    
    # Convert to button states (inverted due to pull-ups)
    buttons_a = [(port_a >> i) & 1 == 0 for i in range(8)]
    buttons_b = [(port_b >> i) & 1 == 0 for i in range(8)]
    
    return buttons_a + buttons_b

# Monitor button presses
while True:
    button_states = check_buttons()
    pressed = [i for i, state in enumerate(button_states) if state]
    
    if pressed:
        print(f"Buttons pressed: {pressed}")
    
    time.sleep(0.1)
```

### Rotary Encoder Operations

```python
from coffee.io.encoder import Encoder
import time

# Initialize encoder with GPIO pins
encoder = Encoder(clk_pin=23, dt_pin=24, sw_pin=25)

# Set up event callbacks
def on_rotation(direction):
    """Handle encoder rotation"""
    if direction > 0:
        print("Rotated clockwise")
    else:
        print("Rotated counter-clockwise")

def on_button_press():
    """Handle encoder button press"""
    print("Encoder button pressed")

def on_button_release():
    """Handle encoder button release"""
    print("Encoder button released")

# Register callbacks
encoder.when_rotated = on_rotation
encoder.when_pressed = on_button_press
encoder.when_released = on_button_release

# Keep program running to receive events
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    encoder.close()
```

### Advanced Scale Features

```python
from coffee.io.scale import Scale
from collections import deque
import statistics

class AdvancedScale(Scale):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.weight_history = deque(maxlen=100)
        self.change_threshold = 5.0  # grams
    
    def detect_weight_events(self):
        """Detect significant weight changes"""
        if len(self.weight_history) < 2:
            return None
        
        current = self.weight_history[-1]
        previous = self.weight_history[-2]
        change = current - previous
        
        if abs(change) > self.change_threshold:
            return {
                'type': 'increase' if change > 0 else 'decrease',
                'amount': abs(change),
                'current_weight': current,
                'previous_weight': previous
            }
        return None
    
    def get_weight_statistics(self):
        """Calculate weight statistics"""
        if not self.weight_history:
            return None
        
        weights = list(self.weight_history)
        return {
            'mean': statistics.mean(weights),
            'median': statistics.median(weights),
            'std_dev': statistics.stdev(weights) if len(weights) > 1 else 0,
            'min': min(weights),
            'max': max(weights),
            'range': max(weights) - min(weights)
        }
    
    def is_weight_stable(self, tolerance=2.0, min_readings=5):
        """Check if weight readings are stable"""
        if len(self.weight_history) < min_readings:
            return False
        
        recent_weights = list(self.weight_history)[-min_readings:]
        weight_range = max(recent_weights) - min(recent_weights)
        return weight_range <= tolerance

# Usage
advanced_scale = AdvancedScale()
advanced_scale.start_reading()

while True:
    # Add reading to history
    weight = advanced_scale.get_latest_reading()
    advanced_scale.weight_history.append(weight)
    
    # Check for events
    event = advanced_scale.detect_weight_events()
    if event:
        print(f"Weight {event['type']}: {event['amount']:.1f}g")
    
    # Check stability
    if advanced_scale.is_weight_stable():
        print(f"Weight stable at {weight:.1f}g")
    
    time.sleep(1)
```

### LCD Animation and Effects

```python
from coffee.io.lcd import LCD
import time
import threading

class AnimatedLCD(LCD):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation_thread = None
        self.stop_animation = threading.Event()
    
    def progress_bar(self, progress, row=1, width=16):
        """Display a progress bar"""
        filled = int(progress * width)
        bar = '█' * filled + '░' * (width - filled)
        
        self.move_to(0, row)
        self.putstr(bar[:width])
    
    def countdown_timer(self, seconds, row=1):
        """Display a countdown timer"""
        for remaining in range(seconds, -1, -1):
            mins, secs = divmod(remaining, 60)
            timer_text = f"Time: {mins:02d}:{secs:02d}"
            
            self.move_to(0, row)
            self.putstr(timer_text.ljust(16))
            time.sleep(1)
    
    def loading_animation(self, message="Loading", row=0, duration=5):
        """Display a loading animation"""
        def animate():
            chars = ['|', '/', '-', '\\']
            start_time = time.time()
            i = 0
            
            while (time.time() - start_time) < duration and not self.stop_animation.is_set():
                display_text = f"{message} {chars[i % len(chars)]}"
                self.move_to(0, row)
                self.putstr(display_text.ljust(16))
                i += 1
                time.sleep(0.2)
        
        self.stop_animation.clear()
        self.animation_thread = threading.Thread(target=animate, daemon=True)
        self.animation_thread.start()
    
    def stop_animations(self):
        """Stop any running animations"""
        self.stop_animation.set()
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=1)

# Usage
animated_lcd = AnimatedLCD()

# Show progress bar
for i in range(101):
    animated_lcd.progress_bar(i / 100)
    time.sleep(0.05)

# Show countdown
animated_lcd.countdown_timer(10)

# Show loading animation
animated_lcd.loading_animation("Processing", duration=3)
time.sleep(3)
animated_lcd.stop_animations()
```

### Button Debouncing and Edge Detection

```python
from coffee.io.multiplex import Multiplex
import time
from collections import defaultdict

class DebouncedButtons(Multiplex):
    def __init__(self, debounce_time=0.05, **kwargs):
        super().__init__(**kwargs)
        self.debounce_time = debounce_time
        self.last_state = [False] * 16
        self.last_change_time = [0] * 16
        self.button_callbacks = {}
    
    def register_button_callback(self, button_id, callback):
        """Register callback for specific button"""
        self.button_callbacks[button_id] = callback
    
    def check_button_changes(self):
        """Check for debounced button state changes"""
        current_time = time.time()
        current_states = self.read_all_buttons()
        
        for i, (current, previous) in enumerate(zip(current_states, self.last_state)):
            time_since_change = current_time - self.last_change_time[i]
            
            # Check if enough time has passed for debouncing
            if time_since_change > self.debounce_time:
                # Detect rising edge (button press)
                if current and not previous:
                    self.on_button_press(i)
                    self.last_change_time[i] = current_time
                
                # Detect falling edge (button release)
                elif not current and previous:
                    self.on_button_release(i)
                    self.last_change_time[i] = current_time
        
        self.last_state = current_states
    
    def on_button_press(self, button_id):
        """Handle button press event"""
        print(f"Button {button_id} pressed")
        if button_id in self.button_callbacks:
            self.button_callbacks[button_id]()
    
    def on_button_release(self, button_id):
        """Handle button release event"""
        print(f"Button {button_id} released")
    
    def read_all_buttons(self):
        """Read state of all 16 buttons"""
        port_a = self.read_port_a()
        port_b = self.read_port_b()
        
        # Convert to boolean states (inverted for pull-ups)
        states = []
        for i in range(8):
            states.append((port_a >> i) & 1 == 0)
        for i in range(8):
            states.append((port_b >> i) & 1 == 0)
        
        return states

# Usage
debounced_buttons = DebouncedButtons()

# Register button callbacks
debounced_buttons.register_button_callback(0, lambda: print("Coffee button pressed!"))
debounced_buttons.register_button_callback(1, lambda: print("Tea button pressed!"))

# Monitor buttons
while True:
    debounced_buttons.check_button_changes()
    time.sleep(0.01)  # 10ms polling
```

## Hardware Interface Patterns

### Error Handling and Recovery

```python
from coffee.io.scale import Scale
from coffee.io.lcd import LCD
import time
import logging

class RobustHardwareInterface:
    def __init__(self):
        self.scale = None
        self.lcd = None
        self.initialize_hardware()
    
    def initialize_hardware(self):
        """Initialize hardware with error handling"""
        try:
            self.scale = Scale()
            self.scale.start_reading()
            logging.info("Scale initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize scale: {e}")
            self.scale = None
        
        try:
            self.lcd = LCD()
            self.lcd.clear()
            self.lcd.putstr("System Ready")
            logging.info("LCD initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize LCD: {e}")
            self.lcd = None
    
    def safe_get_weight(self):
        """Get weight with error handling"""
        if self.scale is None:
            return None
        
        try:
            return self.scale.get_latest_reading()
        except Exception as e:
            logging.error(f"Error reading scale: {e}")
            return None
    
    def safe_display_message(self, message):
        """Display message with error handling"""
        if self.lcd is None:
            print(f"LCD not available, message: {message}")
            return
        
        try:
            self.lcd.clear()
            self.lcd.putstr(message[:32])  # Limit message length
        except Exception as e:
            logging.error(f"Error updating LCD: {e}")
    
    def health_check(self):
        """Check hardware component health"""
        status = {
            'scale': self.scale is not None and self.safe_get_weight() is not None,
            'lcd': self.lcd is not None
        }
        return status
```

For detailed method signatures and class documentation, see the source code using the `:::` directives above.