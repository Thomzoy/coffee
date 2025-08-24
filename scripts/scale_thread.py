from collections import deque
import threading
import time
import signal
import statistics

from typing import Literal

from scale.hx711 import HX711

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

        self.stable_value = 0
    
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
                
                #time.sleep(0.25)  # Wait 1 second
            except Exception as e:
                print(f"Sensor reading error: {e}")
                #time.sleep(0.25)  # Still wait even on error
    
    def read_sensor_value(self):
        """Replace this with your actual sensor reading code"""
        # Placeholder - replace with your HX711 or whatever sensor code
        values = [self.hx.getWeight() for _ in range(self.smoothing_window)]
        if self.smoothing_method == "mean":
            value = statistics.mean(values)
        else:
            value = statistics.median(values)

        previous = self.get_latest_reading()

        delta = value - previous
        if delta < -200:
            # Heuristic to determine that coffee pot was removed
            pass

        readings = self.get_last_readings()
        std = statistics.stdev(readings) if len(readings)>=2 else 0
        print(f"STD: {std:.1f} / Delta: {delta:.1f}")
        return value

    def get_last_readings(self):
        """Get the last N readings (thread-safe)"""
        with self.buffer_lock:
            return list(self.weight_buffer)[:]
    
    def get_latest_reading(self):
        """Get just the most recent reading"""
        with self.buffer_lock:
            return self.weight_buffer[-1] if self.weight_buffer else 0

# Usage example
if __name__ == "__main__":
    sensor = WeightSensor(smoothing_method="median", smoothing_window=5)
    try:
        sensor.start_reading()
        time.sleep(2)
        print("GO")
        from flask import Flask, jsonify, render_template
        import random  # For demo, replace with your HX711 reading

        app = Flask(__name__)

        def read_value():
            # Example: return hx711.get_weight()
            return sensor.read_sensor_value()

        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/data')
        def data():
            value = read_value()
            return jsonify(value=value)
        
        print("Running")
        #app.run(host='0.0.0.0', port=5000, debug=True)
        signal.pause()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        sensor.stop_reading()

"""     
    # Start background reading
    sensor.start_reading()
    
    try:
        # Your main program loop
        while True:
            # Simulate button press or other event
            user_input = input("Press Enter to get readings (or 'q' to quit): ")
            
            if user_input.lower() == 'q':
                break
            
            # Get the last 20 readings
            readings = sensor.get_last_readings()
            print(f"Last {len(readings)} readings: {readings}")
            
            # Or just get the latest
            latest = sensor.get_latest_reading()
            print(f"Latest reading: {latest}")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        sensor.stop_reading() """