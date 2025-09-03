# App Module API

API documentation for the application layer modules that manage the coffee machine interface.

## coffee.app.app

::: coffee.app.app

## coffee.app.page

::: coffee.app.page

## coffee.app.db

::: coffee.app.db

## Usage Examples

### Basic Application Setup

```python
from coffee.app.app import LCDApp
from coffee.app.page import BasePage

# Create and configure the main application
app = LCDApp(
    timeout=15,  # 15 second timeout
    page=BasePage()  # Start with home page
)

# Display the current page
app.display()

# Handle encoder rotation
app.encoder_callback(clockwise=True)

# Handle person button press
app.person_button_callback(button_id=0)
```

### Custom Page Implementation

```python
from coffee.app.page import Page

class CustomPage(Page):
    def __init__(self, custom_data=None):
        super().__init__()
        self.custom_data = custom_data
    
    def display(self):
        """Display custom content on LCD"""
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Custom Page")
        if self.custom_data:
            self.lcd.move_to(0, 1)
            self.lcd.putstr(str(self.custom_data))
    
    def encoder_callback(self, clockwise: bool):
        """Handle encoder rotation"""
        if clockwise:
            return NextCustomPage()
        else:
            return PreviousCustomPage()
    
    def red_button_callback(self):
        """Return to home on red button"""
        return BasePage()
```

### Database Operations

```python
from coffee.app.db import Database

# Initialize database connection
db = Database("coffee_data.db")

# Log coffee consumption
db.log_coffee(
    user_id=1,
    amount_grams=250.5,
    timestamp=datetime.now()
)

# Get user statistics
user_stats = db.get_user_stats(user_id=1)
print(f"Total coffee consumed: {user_stats['total_amount']}g")
print(f"Average per day: {user_stats['daily_average']}g")

# Get recent activity
recent_logs = db.get_recent_coffee_logs(limit=10)
for log in recent_logs:
    print(f"User {log['user_id']}: {log['amount']}g at {log['timestamp']}")
```

### Page Lifecycle Management

```python
class StatefulPage(Page):
    def __init__(self):
        super().__init__()
        self.state = "initial"
        self.data = []
    
    def display(self):
        """Display based on current state"""
        self.lcd.clear()
        if self.state == "initial":
            self.lcd.putstr("Press button")
        elif self.state == "collecting":
            self.lcd.putstr(f"Items: {len(self.data)}")
        elif self.state == "complete":
            self.lcd.putstr("Finished!")
    
    def encoder_button_callback(self):
        """Advance through states"""
        if self.state == "initial":
            self.state = "collecting"
        elif self.state == "collecting":
            self.state = "complete"
        elif self.state == "complete":
            return BasePage()
        
        # Stay on same page but update display
        self.display()
        return self
```

### Event Handling Patterns

```python
from coffee.app.app import set_page

class EventHandlingPage(Page):
    @set_page
    def person_button_callback(self, button_id):
        """Handle person button with automatic page management"""
        # Process the button press
        user_name = self.get_user_name(button_id)
        
        # Show confirmation
        self.display_temporary(
            f"Selected: {user_name}",
            "Confirm?",
            duration=2
        )
        
        # Return new page (decorator handles display update)
        return ConfirmationPage(user_id=button_id)
    
    def get_user_name(self, button_id):
        """Get user name for button ID"""
        # Implementation to retrieve user name
        return f"User {button_id}"
```

### Timeout Handling

```python
class TimeoutAwarePage(Page):
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.custom_timeout = 30  # 30 seconds
    
    def display(self):
        """Show page with timeout indicator"""
        elapsed = time.time() - self.start_time
        remaining = max(0, self.custom_timeout - elapsed)
        
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Timeout Demo")
        self.lcd.move_to(0, 1)
        self.lcd.putstr(f"Time: {remaining:.0f}s")
    
    def timeout_callback(self):
        """Custom timeout behavior"""
        self.display_temporary("Time's up!", duration=1)
        return BasePage()
```

### Error Handling

```python
class RobustPage(Page):
    def encoder_callback(self, clockwise: bool):
        """Safe encoder handling with error recovery"""
        try:
            # Potentially risky operation
            result = self.process_encoder_input(clockwise)
            return result
        except Exception as e:
            # Log error and show user message
            print(f"Error processing encoder: {e}")
            self.display_temporary("Error occurred", "Returning home")
            return BasePage()
    
    def person_button_callback(self, button_id):
        """Validate button ID and handle gracefully"""
        if not self.is_valid_button(button_id):
            self.display_temporary("Invalid button", duration=1)
            return self
        
        return self.handle_valid_button(button_id)
    
    def is_valid_button(self, button_id):
        """Validate button ID is in acceptable range"""
        return 0 <= button_id <= 15
```

## Advanced Features

### Threading Considerations

```python
import threading
from coffee.app.page import Page

class ThreadSafePage(Page):
    def __init__(self):
        super().__init__()
        self.data_lock = threading.Lock()
        self.shared_data = {}
    
    def update_data(self, key, value):
        """Thread-safe data update"""
        with self.data_lock:
            self.shared_data[key] = value
    
    def get_data(self, key):
        """Thread-safe data access"""
        with self.data_lock:
            return self.shared_data.get(key)
    
    def display(self):
        """Display with thread-safe data access"""
        value = self.get_data('display_value')
        if value is not None:
            self.lcd.putstr(str(value))
```

### Background Task Integration

```python
import threading
import time

class BackgroundTaskPage(Page):
    def __init__(self):
        super().__init__()
        self.task_running = False
        self.task_thread = None
    
    def start_background_task(self):
        """Start a background task"""
        if not self.task_running:
            self.task_running = True
            self.task_thread = threading.Thread(
                target=self._background_worker,
                daemon=True
            )
            self.task_thread.start()
    
    def _background_worker(self):
        """Background task implementation"""
        while self.task_running:
            # Do background work
            self.update_display_data()
            time.sleep(1)
    
    def stop_background_task(self):
        """Stop the background task"""
        self.task_running = False
        if self.task_thread and self.task_thread.is_alive():
            self.task_thread.join(timeout=1)
    
    def red_button_callback(self):
        """Clean shutdown on exit"""
        self.stop_background_task()
        return BasePage()
```

### Data Validation and Sanitization

```python
class ValidatedInputPage(Page):
    def __init__(self):
        super().__init__()
        self.input_buffer = ""
        self.max_length = 16  # LCD width
    
    def encoder_callback(self, clockwise: bool):
        """Handle character input with validation"""
        if clockwise:
            char = self.get_next_character()
        else:
            char = self.get_previous_character()
        
        # Validate character
        if self.is_valid_character(char):
            if len(self.input_buffer) < self.max_length:
                self.input_buffer += char
                self.display()
        
        return self
    
    def is_valid_character(self, char):
        """Validate input character"""
        # Allow letters, numbers, and spaces
        return char.isalnum() or char.isspace()
    
    def get_sanitized_input(self):
        """Return sanitized input string"""
        return self.input_buffer.strip()[:self.max_length]
```

For implementation details of specific methods and classes, see the source code documentation using the `:::` directives above.