from collections import deque
import threading
import time
import signal
import statistics

from typing import Literal

from scale.hx711 import HX711

MODES = ["COFFEE_POT_ON", "COFFEE_POT_OFF"]

class WeightSensor:
    def __init__(
        self,
        data_pin: int=17,
        clock_pin: int=27,
        max_readings: int=3,
        smoothing_window: int=3,
        smoothing_method: Literal["mean","median"] = "median",
        reference_unit: float=305.834,
    ):
        self.weight_buffer = deque(maxlen=max_readings)
        self.buffer_lock = threading.Lock()
        self.sensor_thread = None
        self.running = False
        self.smoothing_window = smoothing_window
        self.smoothing_method = smoothing_method

        self.hx = HX711(17, 27)
        self.hx.setReferenceUnit(reference_unit)
        self.hx.setReadingFormat("MSB", "MSB")
        self.hx.autosetOffset()

        self.has_pot = True
        self.update_mug_value = False
        self.stable_value = 0
        self.mug_value = 0
    
    def start_reading(self):
        """Start the sensor reading thread"""
        if self.running:
            return
        
        self.running = True
        self.sensor_thread = threading.Thread(target=self._read_sensor_loop, daemon=True)
        self.sensor_thread.start()
    
    def stop_reading(self):
        """Stop the sensor reading thread"""
        self.running = False
        if self.sensor_thread:
            self.sensor_thread.join()
    
    def _read_sensor_loop(self):
        """Background thread that reads sensor every second"""
        while self.running:
            try:
                # Replace this with your actual sensor reading code
                weight = self.read_sensor_value()
                
                with self.buffer_lock:
                    self.weight_buffer.append(weight)
                
            except Exception as e:
                print(f"Sensor reading error: {e}")

    
    def read_sensor_value(self):
        values = [self.hx.getWeight() for _ in range(self.smoothing_window)]
        if self.smoothing_method == "mean":
            value = statistics.mean(values)
        else:
            value = statistics.median(values)

        previous = self.get_latest_reading()

        delta = value - previous
        if delta < -200:
            # Big negative weight difference: pot is removed
            print(f"Pot is removed - Delta: {delta:.1f}")
            self.has_pot = False

        elif delta > 200:
            # Big positive weight difference: pot is back
            print(f"Pot is back - Delta: {delta:.1f}")
            self.has_pot = True
            self.update_mug_value = True # Update mug weight value with next stable reading

        if self.has_pot:
            readings = self.get_last_readings() + [value]
            std = statistics.stdev(readings) if len(readings)>=2 else None
            #print(f"Has pot, STD: {std}")
            if (std is not None) and (std <= 10):
                new_stable_value = statistics.mean(readings)
                #print(f"New stable value: {new_stable_value}")
                if self.update_mug_value:
                    self.mug_value = self.stable_value - new_stable_value
                    print(f"Mug {self.mug_value}")
                    self.update_mug_value = False
                self.stable_value = new_stable_value

        return value

    def get_last_readings(self):
        """Get the last N readings (thread-safe)"""
        with self.buffer_lock:
            return list(self.weight_buffer)[:]
    
    def get_latest_reading(self):
        """Get just the most recent reading"""
        with self.buffer_lock:
            return self.weight_buffer[-1] if self.weight_buffer else 0

    def get_last_mug_value(self):
        return self.mug_value

# Usage example
if __name__ == "__main__":

    from mcp23017 import *
    from mcp23017.i2c import I2C
    import smbus
    from gpiozero import Button, Device
    from gpiozero.pins.pigpio import PiGPIOFactory
    from signal import pause
    import time

    # Try using pigpio pin factory for better compatibility
    Device.pin_factory = PiGPIOFactory()

    INT_PIN = 4
    button = Button(INT_PIN, pull_up=True, bounce_time=0.2)

    i2c = I2C(smbus.SMBus(1))  # creates an I2C Object as a wrapper for the SMBus
    mcp = MCP23017(0x20, i2c.bus)   # creates an MCP object with the given address

    # Set all as input
    mcp.set_all_input()

    # Enable internal pull-up resistors
    mcp.write(GPPUA, 0xFF)
    mcp.write(GPPUB, 0xFF)

    # Set interrupt comparison to default values
    mcp.write(GPINTENA, 0xFF)
    mcp.write(GPINTENB, 0xFF)

    # Set default value to compare against (all HIGH)
    mcp.write(DEFVALA, 0xFF)
    mcp.write(DEFVALB, 0xFF)

    # Compare to DEFVAL instead of previous value
    mcp.write(INTCONA, 0xFF)
    mcp.write(INTCONB, 0xFF)

    # Enable interrupt mirroring
    mcp.set_interrupt_mirror(True)

    # Enable open-drain for interrupt output pin
    mcp.set_bit_enabled(IOCONA, ODR_BIT, True)
    mcp.set_bit_enabled(IOCONB, ODR_BIT, True)

    def pressed_button_id(flags_a, flags_b):
        flags = flags_a + flags_b
        try:
            return flags.index("1")
        except ValueError:
            raise ValueError("No button was pressed")
    
    sensor = WeightSensor(smoothing_method="median", smoothing_window=5)

    def interrupt_callback():
        print("Interrupt detected!")
        flags_a, flags_b = mcp.read_interrupt_flags()
        caps_a, caps_b = mcp.read_interrupt_captures()

        print("Pressed: ", pressed_button_id(flags_a, flags_b))
        print(f"Mug: {sensor.get_last_mug_value()}")

        # Reset interrupt by reading all pins
        mcp.digital_read_all()

    # Attach the interrupt
    button.when_pressed = interrupt_callback

    try:
        sensor.start_reading()
        time.sleep(2)
        print("GO")
        signal.pause()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        sensor.stop_reading()
