# Calibration Guide

Proper calibration is essential for accurate weight measurements. This guide covers all aspects of calibrating your coffee machine scale.

## Overview

The coffee machine uses HX711 load cell amplifiers with four load cells arranged in a Wheatstone bridge configuration. Calibration involves:

1. **Offset calibration** - Setting the zero point
2. **Reference unit calibration** - Setting the weight scale factor
3. **Validation** - Verifying accuracy across the measurement range

## When to Calibrate

### Initial Setup
- First installation of the system
- After replacing any load cells
- After changing the HX711 amplifier

### Periodic Recalibration
- Monthly for high-precision requirements
- Quarterly for normal use
- When accuracy seems degraded

### After Hardware Changes
- Moving the coffee machine
- Replacing or adjusting the platform
- Temperature changes in environment
- Electrical interference issues

## Pre-Calibration Checklist

Before starting calibration, ensure:

- [ ] All hardware connections are secure
- [ ] Load cells are properly mounted and level
- [ ] Platform is stable and not touching other surfaces
- [ ] Known calibration weights are available (1kg recommended)
- [ ] System has been powered on for 5+ minutes (warm-up)
- [ ] No vibrations or air currents affecting the scale

## Calibration Process

### Method 1: Automatic Calibration Script

Use the built-in calibration script for guided calibration:

```bash
cd /path/to/coffee
python scripts/calibrate.py
```

Follow the on-screen prompts:

1. **Remove all weight** from the scale
   ```
   Remove all weight from scale and press ENTER...
   Current reading: 12450 (should be close to 0)
   ```

2. **Place known weight** (1kg recommended)
   ```
   Place 1000g on scale and press ENTER...
   Current reading: 114852
   Enter actual weight in grams: 1000
   ```

3. **Calculate reference unit**
   ```
   Calculated reference unit: 114.852
   Testing with new calibration...
   Weight reading: 999.2g (Target: 1000g)
   Save calibration? (y/n): y
   ```

### Method 2: Manual Calibration

For more control over the calibration process:

```python
from coffee.io.scale import Scale
import time

# Initialize scale
scale = Scale()
scale.start_reading()
time.sleep(2)  # Allow stabilization

# Step 1: Zero calibration
print("Remove all weight from scale...")
input("Press ENTER when ready...")

# Read multiple samples for stability
readings = []
for i in range(10):
    reading = scale.read_raw_value()
    readings.append(reading)
    time.sleep(0.1)

offset = sum(readings) / len(readings)
scale.set_offset(offset)
print(f"Offset set to: {offset}")

# Step 2: Reference unit calibration
print("Place 1000g on scale...")
input("Press ENTER when ready...")

# Read with known weight
readings = []
for i in range(10):
    reading = scale.read_raw_value()
    readings.append(reading)
    time.sleep(0.1)

raw_with_weight = sum(readings) / len(readings)
known_weight = 1000.0  # grams

# Calculate reference unit
reference_unit = (raw_with_weight - offset) / known_weight
scale.set_reference_unit(reference_unit)
print(f"Reference unit set to: {reference_unit}")

# Step 3: Validation
print("Validation readings:")
for i in range(5):
    weight = scale.get_weight()
    print(f"Reading {i+1}: {weight:.1f}g")
    time.sleep(1)

scale.stop_reading()
```

### Method 3: Multi-Point Calibration

For highest accuracy, use multiple calibration points:

```python
def multi_point_calibration():
    """Perform multi-point calibration for better accuracy"""
    
    scale = Scale()
    scale.start_reading()
    time.sleep(2)
    
    # Calibration points (weight in grams)
    cal_points = [0, 250, 500, 750, 1000, 1500, 2000]
    raw_readings = []
    
    for weight in cal_points:
        if weight == 0:
            print("Remove all weight from scale...")
        else:
            print(f"Place {weight}g on scale...")
        
        input("Press ENTER when ready...")
        
        # Take multiple readings
        readings = []
        for i in range(20):
            reading = scale.read_raw_value()
            readings.append(reading)
            time.sleep(0.05)
        
        # Use median to reduce noise
        import statistics
        median_reading = statistics.median(readings)
        raw_readings.append((weight, median_reading))
        print(f"Raw reading for {weight}g: {median_reading}")
    
    # Calculate best-fit line using least squares
    import numpy as np
    weights = np.array([point[0] for point in raw_readings])
    raw_vals = np.array([point[1] for point in raw_readings])
    
    # Linear regression: raw = offset + reference_unit * weight
    coeffs = np.polyfit(weights, raw_vals, 1)
    reference_unit = coeffs[0]
    offset = coeffs[1]
    
    print(f"Calculated offset: {offset}")
    print(f"Calculated reference unit: {reference_unit}")
    
    # Validate calibration
    print("\nValidation:")
    for weight, raw in raw_readings:
        calculated_raw = offset + reference_unit * weight
        error = abs(raw - calculated_raw)
        print(f"Weight: {weight}g, Raw: {raw}, Calc: {calculated_raw:.0f}, Error: {error:.0f}")
    
    # Apply calibration
    scale.set_offset(offset)
    scale.set_reference_unit(1.0 / reference_unit)  # Invert for HX711 library
    
    scale.stop_reading()
    return offset, reference_unit
```

## Calibration Weights

### Recommended Weights

**Primary Calibration:**
- 1000g (1kg) - Main calibration weight
- Should be certified or accurately known

**Validation Weights:**
- 250g - Quarter scale
- 500g - Half scale  
- 750g - Three-quarters scale
- 1500g - Over scale

### DIY Calibration Weights

If certified weights aren't available:

**Water Method:**
- 1000ml water = 1000g (at 20°C)
- Use graduated cylinder for accuracy
- Account for container weight

**Coin Method:**
- US Nickel: 5.000g
- US Quarter: 5.670g  
- Euro 2€ coin: 8.500g
- Multiple coins for larger weights

**Food Items:**
- Sugar: 1 cup = ~200g
- Flour: 1 cup = ~125g
- Rice: 1 cup = ~190g
- Weigh on accurate kitchen scale first

## Troubleshooting Calibration Issues

### Unstable Readings

**Symptoms:**
- Large variations between consecutive readings
- Readings drift continuously
- Cannot achieve stable baseline

**Solutions:**
```bash
# Check for mechanical issues
# - Ensure platform is level
# - Check for binding or friction
# - Verify load cells are not overloaded

# Check electrical connections
# - Verify HX711 wiring
# - Check for loose connections
# - Test with multimeter

# Software solutions
# Increase smoothing window
NUM_SCALE_READINGS = 10  # Instead of 5
LEN_SCALE_BUFFER = 5     # Instead of 3
```

### Offset Drift

**Symptoms:**
- Zero point changes over time
- Negative weights when scale is empty
- Systematic bias in measurements

**Solutions:**
```python
# Auto-zero correction
def auto_zero_correction(scale, threshold=5.0):
    """Automatically correct zero drift"""
    current_reading = scale.get_weight()
    
    if abs(current_reading) < threshold:
        # Small reading when empty - adjust offset
        new_offset = scale.get_offset() + current_reading
        scale.set_offset(new_offset)
        print(f"Auto-corrected offset by {current_reading:.1f}g")

# Periodic re-calibration
def check_calibration_accuracy(scale, known_weight=1000):
    """Check if calibration is still accurate"""
    print(f"Place {known_weight}g on scale for accuracy check...")
    input("Press ENTER when ready...")
    
    measured_weight = scale.get_weight()
    error_percent = abs(measured_weight - known_weight) / known_weight * 100
    
    if error_percent > 2:  # 2% tolerance
        print(f"Calibration error: {error_percent:.1f}% - Recalibration recommended")
        return False
    else:
        print(f"Calibration accuracy: {error_percent:.1f}% - Good")
        return True
```

### Non-Linear Response

**Symptoms:**
- Accurate at some weights, inaccurate at others
- Consistent bias in one direction
- Calibration doesn't improve accuracy

**Solutions:**
```python
# Implement polynomial calibration
def polynomial_calibration(raw_readings, weights, degree=2):
    """Use polynomial fit for non-linear response"""
    import numpy as np
    
    raw_vals = np.array([r[1] for r in raw_readings])
    weight_vals = np.array([r[0] for r in raw_readings])
    
    # Fit polynomial
    coeffs = np.polyfit(raw_vals, weight_vals, degree)
    
    def convert_reading(raw_value):
        """Convert raw reading to calibrated weight"""
        return np.polyval(coeffs, raw_value)
    
    return convert_reading

# Use lookup table for extreme non-linearity
class LookupTableCalibration:
    def __init__(self, calibration_points):
        self.points = sorted(calibration_points)  # (raw, weight) pairs
    
    def interpolate_weight(self, raw_value):
        """Interpolate weight from raw value using calibration table"""
        # Find bracketing points
        for i in range(len(self.points) - 1):
            raw1, weight1 = self.points[i]
            raw2, weight2 = self.points[i + 1]
            
            if raw1 <= raw_value <= raw2:
                # Linear interpolation
                ratio = (raw_value - raw1) / (raw2 - raw1)
                return weight1 + ratio * (weight2 - weight1)
        
        # Extrapolation
        if raw_value < self.points[0][0]:
            return self.points[0][1]  # Use first point
        else:
            return self.points[-1][1]  # Use last point
```

## Validation and Testing

### Accuracy Testing

```python
def test_calibration_accuracy(scale):
    """Comprehensive calibration accuracy test"""
    
    test_weights = [100, 250, 500, 750, 1000, 1250, 1500]
    results = []
    
    print("Calibration Accuracy Test")
    print("=" * 40)
    
    for target_weight in test_weights:
        print(f"\nPlace {target_weight}g on scale...")
        input("Press ENTER when ready...")
        
        # Take multiple readings
        readings = []
        for i in range(10):
            reading = scale.get_weight()
            readings.append(reading)
            time.sleep(0.1)
        
        # Statistics
        import statistics
        avg_reading = statistics.mean(readings)
        std_dev = statistics.stdev(readings) if len(readings) > 1 else 0
        error = avg_reading - target_weight
        error_percent = (error / target_weight) * 100
        
        results.append({
            'target': target_weight,
            'measured': avg_reading,
            'error': error,
            'error_percent': error_percent,
            'std_dev': std_dev
        })
        
        print(f"Target: {target_weight}g")
        print(f"Measured: {avg_reading:.1f}g ± {std_dev:.1f}g")
        print(f"Error: {error:.1f}g ({error_percent:.1f}%)")
    
    # Summary
    print(f"\nCalibration Test Summary")
    print("=" * 40)
    errors = [abs(r['error_percent']) for r in results]
    max_error = max(errors)
    avg_error = sum(errors) / len(errors)
    
    print(f"Maximum error: {max_error:.1f}%")
    print(f"Average error: {avg_error:.1f}%")
    
    if max_error < 2:
        print("✓ Calibration PASSED (< 2% error)")
    elif max_error < 5:
        print("⚠ Calibration MARGINAL (2-5% error)")
    else:
        print("✗ Calibration FAILED (> 5% error)")
    
    return results
```

### Repeatability Testing

```python
def test_repeatability(scale, test_weight=1000, num_tests=20):
    """Test measurement repeatability"""
    
    print(f"Repeatability Test with {test_weight}g")
    print("Remove and replace weight for each test")
    
    measurements = []
    
    for i in range(num_tests):
        print(f"\nTest {i+1}/{num_tests}")
        print("Remove weight...")
        input("Press ENTER when weight is removed...")
        
        time.sleep(1)  # Allow settling
        
        print(f"Place {test_weight}g on scale...")
        input("Press ENTER when weight is placed...")
        
        time.sleep(2)  # Allow settling
        measurement = scale.get_weight()
        measurements.append(measurement)
        
        print(f"Reading: {measurement:.1f}g")
    
    # Calculate statistics
    import statistics
    mean_val = statistics.mean(measurements)
    std_dev = statistics.stdev(measurements)
    coefficient_of_variation = (std_dev / mean_val) * 100
    
    print(f"\nRepeatability Results:")
    print(f"Mean: {mean_val:.1f}g")
    print(f"Standard deviation: {std_dev:.1f}g")
    print(f"Coefficient of variation: {coefficient_of_variation:.1f}%")
    print(f"Range: {min(measurements):.1f}g - {max(measurements):.1f}g")
    
    if std_dev < 2:
        print("✓ Repeatability EXCELLENT (< 2g std dev)")
    elif std_dev < 5:
        print("⚠ Repeatability GOOD (2-5g std dev)")
    else:
        print("✗ Repeatability POOR (> 5g std dev)")
    
    return measurements
```

## Saving and Loading Calibration

### Calibration Data Storage

```python
import json
from datetime import datetime

class CalibrationManager:
    def __init__(self, filename='calibration.json'):
        self.filename = filename
    
    def save_calibration(self, offset, reference_unit, validation_data=None):
        """Save calibration data to file"""
        calibration_data = {
            'timestamp': datetime.now().isoformat(),
            'offset': offset,
            'reference_unit': reference_unit,
            'validation': validation_data or [],
            'version': '1.0'
        }
        
        with open(self.filename, 'w') as f:
            json.dump(calibration_data, f, indent=2)
        
        print(f"Calibration saved to {self.filename}")
    
    def load_calibration(self):
        """Load calibration data from file"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            print(f"Calibration loaded from {data['timestamp']}")
            return data['offset'], data['reference_unit']
        
        except FileNotFoundError:
            print("No calibration file found - using defaults")
            return 0, 305.834  # Default values
        
        except json.JSONDecodeError:
            print("Invalid calibration file - using defaults")
            return 0, 305.834
    
    def backup_calibration(self):
        """Create backup of current calibration"""
        import shutil
        backup_name = f"calibration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(self.filename, backup_name)
        print(f"Calibration backed up to {backup_name}")

# Usage
cal_manager = CalibrationManager()

# Save calibration
cal_manager.save_calibration(
    offset=12450,
    reference_unit=114.852,
    validation_data=test_results
)

# Load calibration
offset, ref_unit = cal_manager.load_calibration()
```

## Best Practices

### Environmental Considerations

- **Temperature stability** - Allow 30-minute warmup
- **Vibration isolation** - Avoid mechanical vibrations
- **Air currents** - Shield from drafts
- **Electrical interference** - Keep away from motors/transformers

### Maintenance Schedule

**Weekly:**
- Check zero reading
- Verify with known weight

**Monthly:**
- Full recalibration if accuracy degraded
- Clean load cell connections

**Quarterly:**
- Complete calibration validation
- Backup calibration data

**Annually:**
- Professional calibration verification
- Replace calibration weights if worn

For hardware troubleshooting during calibration, see the [Troubleshooting Guide](troubleshooting.md).