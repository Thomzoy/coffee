import time
import statistics
import threading
import multiprocessing as mp
from collections import deque
from typing import Any, Callable, Literal, Optional

import HX711

from coffee.app.page import Page
from coffee.config import POT_WEIGHT_THRESHOLD, NUM_SCALE_READINGS, LEN_SCALE_BUFFER


class Scale:
    """
    HX711-based weight scale sensor with callback functionality.

    Manages weight readings, detects pot removal/placement, and triggers
    callbacks for mug serving events. Runs sensor reading in a background process.
    """

    def __init__(
        self,
        data_pin: int = 17,
        clock_pin: int = 27,
        reference_unit: int = 304, # Value obtained by weighting a known weight
        offset: int = 1581736, # We don't care since we only measure delta
        served_mug_callback: Optional[Callable[[float], Page | None]] = None,
        removed_pot_callback: Optional[Callable[[], Page | None]] = None,
    ):

        self.served_mug_callback: Optional[Callable[[float], Page | None]] = (
            served_mug_callback
        ) # Called when meaningful mug value is measured
        self.removed_pot_callback: Optional[Callable[[], Page | None]] = (
            removed_pot_callback
        ) # Called when pot is removed from the scale

        self.hx = HX711.SimpleHX711(
            data_pin,
            clock_pin,
            reference_unit,
            offset,
            HX711.Rate.HZ_80,
        )
        self.hx.setUnit(HX711.Mass.Unit.G)
        self.hx.zero()

        self.has_pot = True # Flag to store if pot is on the scale or not
        self.update_mug_value = False # Flag to tell if the weight of the mug should be measured
        self.stable_value = 0 # Last stable measured weight
        self.mug_value = 0 # Last measured mug value

        # Signal for particular events
        self.signals = dict(
            POT_OFF = mp.Event(), # Pot is off    
            POT_ON = mp.Event(), # Pot is back on
        )
        for signal in self.signals.values():
            signal.set()

        # Placeholder for future process worker
        self.pw = None
        self.stop_event = mp.Event()

    @staticmethod
    def writer(stack, hx, signals, stop_event):
        while not stop_event.is_set():
            with mp.Lock():
                value = float(hx.weight(NUM_SCALE_READINGS))
                delta = value - stack[-1] if stack else 0
                signal = None
                if delta <= -POT_WEIGHT_THRESHOLD:
                    # Big negative weight difference: pot is removed
                    signal = signals["POT_OFF"]
                elif delta >= POT_WEIGHT_THRESHOLD:
                    # Big positive weight difference: pot is back
                    signal = signals["POT_ON"]
                
                if len(stack) >= LEN_SCALE_BUFFER:
                    stack.pop(0)  # discard oldest
                stack.append(value)  # push new value
            
            if signal is not None:
                signal.clear()
                signal.wait()
                signal.set()

    def start_reading(self):
        self.manager = mp.Manager()
        self.stack = self.manager.list()

        self.pw = mp.Process(
            target=Scale.writer,
            args=(self.stack, self.hx, self.signals, self.stop_event)
        )
        self.pw.start()

    def read(self):
        readings = [v for v in self.stack]
        if len(readings) < 2: # Only happens at beginning
            return

        delta = readings[-1] - readings[-2]
        if not self.signals["POT_OFF"].is_set():
            print(f"Pot is removed - Delta: {delta:.1f}")
            self.has_pot = False
            if self.removed_pot_callback is not None:
                self.removed_pot_callback()
            self.signals["POT_OFF"].set()

        elif not self.signals["POT_ON"].is_set():
            print(f"Pot is back - Delta: {delta:.1f}")
            self.has_pot = True
            self.update_mug_value = (
                True  # Update mug weight value with next stable reading
            )
            self.signals["POT_ON"].set()

        if self.has_pot:
            std = statistics.stdev(readings)
            # print(f"Has pot, STD: {std}")
            if (std is not None) and (std <= 5):
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

        return self.mug_value

    def stop_reading(self):
        """Stop the sensor reading process"""
        self.stop_event.set()
        if self.pw is not None:
            print("Scale process terminate")
            self.pw.terminate()
            print("Scale process join")
            self.pw.join()
        print("Manager shutdown")
        self.manager.shutdown()
        print("HX711 shutdown")
        self.hx.powerDown()
        self.hx.disconnect()

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
