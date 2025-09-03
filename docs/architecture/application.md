
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

#### How it works
* The app displays the page stored in `self.page` by calling `self.page.display()`
* It can dispatch some events to the current page via **callbacks**: For instance, when the rotary encoder is turned, the `encoder_callback` to the current page (at `self.page`) is called
* Each of the app's callback is decorated with the `@set_page` decorator. This decorator checks the return value of the **page** callback. If it returns a `Page`, the return value is used to set the current `self.page` and is then displayed. Else (any other value), the current page is kept and is displayed again

Example: 

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

* Available callbacks:
     * `encoder_callback(self, clockwise: bool)`: when the rotary encoder is turned
     * `encoder_button_callback(self)`: when the rotary encoder button is pressed
     * `red_button_callback(self)`: when the red button is pressed
     * `person_button_callback(self, button_id)`: when a person button is pressed
     * `removed_pot_callback(self)`: when the coffee pot was removed (drop of weight)
     * `served_mug_callback(self, mug_value: float)`: when a mug was served (i.e., the scale detected a weight increase after the pot was removed). `mug_value` holds the weight (gr) of the mug


### Page System (`coffee.app.page`)


**Page**
- Defines the interface for all pages
- Provides default implementations for callbacks
- Manages LCD display operations
- Handles timeout behavior

See [here][page-types] for all page types

### Database Module (`coffee.app.db`)

Manages data persistence using SQLite.

## Configuration Component

### Config Module (`coffee.config`)

Centralized configuration management for the entire system.
