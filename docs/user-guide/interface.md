# User Interface Guide

Learn how to navigate and use the coffee machine LCD interface effectively.

## Interface Overview

The coffee machine features a 16x2 character LCD display with a rotary encoder for navigation and multiple user buttons for interaction.

### Control Elements

- **LCD Display:** 16 characters × 2 lines with backlight
- **Rotary Encoder:** Turn to navigate, press to select
- **Red Button:** Cancel/back button  
- **Person Buttons (0-15):** Individual user assignment buttons

### Navigation Principles

The interface follows these principles:
- **Turn encoder** to navigate between options
- **Press encoder** to select/confirm
- **Red button** to cancel or go back
- **Person buttons** to assign coffee consumption

## Page Types

### Home Page (BasePage)

The default screen that displays when the system is idle.

```
┌────────────────┐
│ Bonjour !!     │
│                │
└────────────────┘
```

**Available Actions:**
- Turn encoder → Go to Menu
- Press person button → View person info
- Coffee serving detected → Automatic transition to Mug Page

### Menu Page

Accessed by turning the encoder from the home page.

```
┌────────────────┐
│ Menu           │
│ > Nommer bouton│
└────────────────┘
```

**Navigation:**
- Turn encoder → Scroll through menu items
- Press encoder → Select highlighted item
- Red button → Return to home

**Menu Items:**
- **Nommer bouton** - Assign names to user buttons

### Person Page

Displays information about a specific user when their button is pressed.

```
┌────────────────┐
│ Thomas         │
│ 2.3kg aujourd  │
└────────────────┘
```

Shows:
- User name (or "Utilisateur X" if not named)
- Daily coffee consumption
- Total consumption statistics

**Actions:**
- Red button → Return to home
- Timeout → Automatic return to home

### Mug Page

Appears automatically when coffee serving is detected.

```
┌────────────────┐
│ Mug: 245g      │
│ Qui?           │
└────────────────┘
```

**Information Displayed:**
- Amount of coffee served (in grams)
- Prompt asking who consumed the coffee

**Actions:**
- Press person button → Assign coffee to that person
- Red button → Cancel assignment
- Encoder button → Confirm assignment to pre-selected users

### Name Button Page

Used to assign names to user buttons.

```
┌────────────────┐
│ Button 0       │
│ Name: A_       │
└────────────────┘
```

**Character Selection:**
- Turn encoder → Scroll through characters (A-Z, 0-9, space)
- Press encoder → Select current character
- Navigate to ↵ symbol → Confirm name entry
- Red button → Cancel naming

## Coffee Workflow

### Normal Coffee Serving

1. **Remove coffee pot** from the scale
   ```
   ┌────────────────┐
   │ Pot removed    │
   │ Waiting...     │
   └────────────────┘
   ```

2. **Serve coffee** into mugs (add weight to scale)

3. **Return pot** to scale - system detects serving
   ```
   ┌────────────────┐
   │ Mug: 245g      │
   │ Qui?           │
   └────────────────┘
   ```

4. **Press person button** to assign coffee
   ```
   ┌────────────────┐
   │ Thomas: 245g   │
   │ Enregistré!    │
   └────────────────┘
   ```

5. **Return to home** automatically

### Multi-User Assignment

If multiple people drank coffee from the same serving:

1. **First person** presses their button
   ```
   ┌────────────────┐
   │ Thomas: 122g   │
   │ Encore?        │
   └────────────────┘
   ```

2. **Additional people** press their buttons
   ```
   ┌────────────────┐
   │ Marie: 123g    │
   │ Fini!          │
   └────────────────┘
   ```

3. System automatically divides the total amount

### Pre-Assignment Feature

Users can press their buttons **before** serving coffee:

1. **Press person button** (up to 15 seconds before serving)
2. **Remove pot and serve coffee**
3. **Return pot** - coffee is automatically assigned to pre-selected users

## Button Management

### Assigning Names to Buttons

1. **From home page**, turn encoder to access menu
2. **Select "Nommer bouton"**
3. **Press the button** you want to name
4. **Enter the name** using character selection:
   - Turn encoder to scroll through A-Z, 0-9, space
   - Press encoder to select each character
   - Navigate to ↵ (enter symbol) to finish

### Character Input Guide

The character selection follows this order:
```
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
0 1 2 3 4 5 6 7 8 9
[space] ↵
```

- **Letters A-Z:** User names
- **Numbers 0-9:** Can be used in names
- **Space:** For multi-word names
- **↵ (Enter):** Confirms the name

## Display Features

### Text Scrolling

Long messages automatically scroll across the display:

```
Initial: "This is a very long..."
After 1s: "is is a very long me..."
After 2s: "s is a very long mess..."
```

### Custom Symbols

The display can show special characters:
- **↵** - Enter/confirm symbol
- **Custom icons** - Coffee cup, user symbols, etc.

### Backlight Management

- **Automatic on** when interaction occurs
- **Dims after inactivity** to save power
- **Brightness adjustment** based on ambient light (if sensor present)

## Timeout Behavior

### Automatic Returns

The system automatically returns to the home page after:
- **15 seconds** of inactivity on any page
- **Menu timeout** if no selection is made
- **Completion** of coffee assignment

### Timeout Indicators

Some pages show countdown timers:
```
┌────────────────┐
│ Menu (12s)     │
│ > Nommer bouton│
└────────────────┘
```

## Error Messages

### Common Error Displays

**Scale Error:**
```
┌────────────────┐
│ Scale Error    │
│ Check hardware │
└────────────────┘
```

**Button Error:**
```
┌────────────────┐
│ Button Error   │
│ Try again      │
└────────────────┘
```

**Database Error:**
```
┌────────────────┐
│ Save Failed    │
│ Data lost      │
└────────────────┘
```

### Recovery Actions

- **Hardware errors** - Check connections and restart
- **Software errors** - System automatically recovers to home page
- **Data errors** - Try operation again

## Accessibility Features

### Visual Indicators

- **High contrast** text for readability
- **Clear fonts** optimized for LCD display
- **Consistent layout** across all pages

### Tactile Feedback

- **Physical buttons** with distinct feel
- **Rotary encoder clicks** for positive feedback
- **Audible confirmation** (if speaker connected)

### Large Text Mode

For users with vision difficulties:
```
┌────────────────┐
│    THOMAS      │
│     2.3kg      │
└────────────────┘
```

## Tips and Shortcuts

### Quick Operations

- **Double-click encoder** on home page → Quick menu access
- **Hold red button** for 3 seconds → System information
- **Press multiple person buttons** → Multi-user assignment

### Efficiency Tips

1. **Pre-assign buttons** before serving to speed up workflow
2. **Use consistent naming** for easy recognition
3. **Learn the menu layout** to navigate quickly
4. **Monitor daily totals** to track consumption

### Troubleshooting Quick Fixes

- **Garbled display** → Red button to refresh
- **Stuck on page** → Hold red button to force home
- **No response** → Check if system is processing (blinking backlight)

## Advanced Features

### Statistics Display

Hold encoder button on Person Page for detailed stats:
```
┌────────────────┐
│ Thomas - Stats │
│ Week: 1.2kg    │
└────────────────┘
```

### System Information

From home page, hold red button for 3 seconds:
```
┌────────────────┐
│ Coffee v1.0.0  │
│ Uptime: 2d 3h  │
└────────────────┘
```

### Calibration Mode

Access through hidden menu combination:
```
┌────────────────┐
│ Calibration    │
│ Place 1kg      │
└────────────────┘
```

## Customization Options

### Display Preferences

- **Language selection** (if multiple languages supported)
- **Units** (grams vs ounces)
- **Date format** (12/24 hour, date format)

### Behavior Settings

- **Timeout duration** (5-60 seconds)
- **Auto-assignment** threshold
- **Confirmation prompts** (enable/disable)

For troubleshooting display issues, see the [Troubleshooting Guide](troubleshooting.md).