import time
import statistics
import threading
from collections import deque
from typing import Any, Callable, Literal, Optional

import HX711

from coffee.app.page import Page


MODES = ["COFFEE_POT_ON", "COFFEE_POT_OFF"]


class Scale:
    """
    HX711-based weight scale sensor with callback functionality.

    Manages weight readings, detects pot removal/placement, and triggers
    callbacks for mug serving events. Runs sensor reading in a background thread.
    """

    def __init__(
        self,
        data_pin: int = 17,
        clock_pin: int = 27,
        max_readings: int = 3,
        smoothing_window: int = 3,
        reference_unit: int = 304,
        offset: int = 1581736,
        served_mug_callback: Optional[Callable[[float], Page | None]] = None,
        removed_pot_callback: Optional[Callable[[], Page | None]] = None,
    ):
        self.weight_buffer = deque(maxlen=max_readings)
        self.buffer_lock = threading.Lock()
        self.sensor_thread = None
        self.running = False
        self.smoothing_window = smoothing_window

        self.served_mug_callback: Optional[Callable[[float], Page | None]] = (
            served_mug_callback
        )
        self.removed_pot_callback: Optional[Callable[[], Page | None]] = (
            removed_pot_callback
        )

        self.hx = HX711.SimpleHX711(
            data_pin,
            clock_pin,
            reference_unit,
            offset,
            HX711.Rate.HZ_10,
        )
        self.hx.setUnit(HX711.Mass.Unit.G)
        self.hx.zero()

        self.has_pot = True
        self.update_mug_value = False
        self.stable_value = 0
        self.mug_value = 0

    def start_reading(self):
        """Start the sensor reading thread"""
        if self.running:
            return

        self.running = True
        self.sensor_thread = threading.Thread(
            target=self._read_sensor_loop, daemon=True
        )
        self.sensor_thread.start()

    def stop_reading(self):
        """Stop the sensor reading thread"""
        self.running = False
        if self.sensor_thread:
            self.sensor_thread.join()
        self.hx.disconnect()
        self.hx.powerDown()

    def _read_sensor_loop(self):
        """Background thread that reads sensor every second"""
        while self.running:
            try:
                weight = self.read_sensor_value()

                with self.buffer_lock:
                    self.weight_buffer.append(weight)

                time.sleep(1)

            except Exception as e:
                print(f"Sensor reading error: {e}")

    def read_sensor_value(self) -> float:
        """
        Read and process a single sensor value.

        Takes multiple readings, applies smoothing, detects pot changes,
        and triggers callbacks for mug events.

        Returns:
            The processed weight value
        """

        value = float(self.hx.weight(self.smoothing_window))
        #print("Weight: ", value)

        previous = self.get_latest_reading()

        delta = value - previous
        if delta < -100:
            # Big negative weight difference: pot is removed
            print(f"Pot is removed - Delta: {delta:.1f}")
            self.has_pot = False
            if self.removed_pot_callback is not None:
                self.removed_pot_callback()

        elif (delta > 100):
            # Big positive weight difference: pot is back
            print(f"Pot is back - Delta: {delta:.1f}")
            self.has_pot = True
            self.update_mug_value = (
                True  # Update mug weight value with next stable reading
            )

        if self.has_pot:
            readings = self.get_last_readings() + [value]
            std = statistics.stdev(readings) if len(readings) >= 2 else None
            # print(f"Has pot, STD: {std}")
            if (std is not None) and (std <= 10):
                new_stable_value = statistics.mean(readings)
                # print(f"New stable value: {new_stable_value}")
                if self.update_mug_value:
                    self.mug_value = self.stable_value - new_stable_value
                    print(f"Mug {self.mug_value}")
                    if (self.mug_value > 15) and (self.mug_value < 500):
                        # Between 15g and 500G, we consider it's a mug
                        if self.served_mug_callback is not None:
                            self.served_mug_callback(self.mug_value)
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

    def get_last_mug_value(self) -> float:
        """Get the weight of the last served mug."""
        return self.mug_value

    def set_served_mug_callback(
        self, served_mug_callback: Optional[Callable[[float], Page | None]]
    ):
        self.served_mug_callback = served_mug_callback

    def set_removed_pot_callback(
        self, removed_pot_callback: Optional[Callable[[], Page | None]]
    ):
        self.removed_pot_callback: Optional[Callable[[], Any]] = removed_pot_callback
