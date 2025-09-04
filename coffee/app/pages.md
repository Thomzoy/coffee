# Page Types

Here are all the pages you might encounter

## HomePage

The default screen that displays when the system is idle.

```
┌────────────────┐
│ Bonjour !!     │
│                │
└────────────────┘
```

??? tip "**Available Actions:**"
    - Turn encoder → Go to Menu
    - Press person button → View person info
    - Coffee serving detected → Automatic transition to Mug Page
    - Timeout → Turn screen off

## MenuPage

Accessed by turning the encoder from the home page.

```
┌────────────────┐
│ Menu           │
│ > Nommer bouton│
└────────────────┘
```

??? tip "**Available Actions:**"
    - Turn encoder → Scroll through menu items
    - Press encoder → Select highlighted item
    - Red button → Return to home
    - Timeout → Automatic return to home

**The following menu items are available:**

### NameButtonPage

Used to assign names to user buttons. When clicked, asks to press the button to assign. Then:

```
┌────────────────┐
│ Button 0       │
│ MIC_           │
└────────────────┘
```

??? tip "**Available Actions:**"
    - Turn encoder → Scroll through characters (A-Z, 0-9, space)
    - Press encoder → Select current character
    - Navigate to "↵" symbol (after Z) → Confirm name entry
    - Red button → Cancel naming and return to home
    - Timeout → Automatic return to home


### StatsPage

Shows the total number (sum on all users) of mugs served, and total volume

```
┌────────────────┐
│ 5 tasses       │
│ 1.21 L         │
└────────────────┘
```

??? tip "**Available Actions:**"
    - Red button → Return to home
    - Timeout → Automatic return to home

### HomePage

Turn the Raspberry off

```
┌────────────────┐
│ Shutdown ...   │
│                │
└────────────────┘
```

!!! warning
    This doesn't switch off the power to the LCD, although it will be turned of by software before shutting down

### RestartPage


Restart the Raspberry

```
┌────────────────┐
│ Restart ...    │
│                │
└────────────────┘
```

### HostnamePage


Displays the hostname

```
┌────────────────┐
│ Hostname       │
│ 192.168.1.10   │
└────────────────┘
```

## Person Page

Displays information about a specific user when their button is pressed.

```
┌──────────────────────┐
│ Michael              │
│ Ajd: 1 tasse - 30mL  │
└──────────────────────┘
```

Shows:
- User name (or the button ID if not named)
- Coffee consumption of the current day

??? tip "**Available Actions:**"
    - Red button → Return to home
    - Timeout → Automatic return to home

## Mug Page

Appears automatically when coffee serving is detected.

### Mug page - Serving

When the coffee pot is removed

```
┌───────────────────┐
│ Service ...       │
│                   │
└───────────────────┘
```

**Information Displayed:**
- Blinking "Service ..."

### Mug page - Served

When the coffee pot is back and a mug was served

```
┌───────────────────┐
│ 75mL - Qui ?      │
│                   │
└───────────────────┘
```

**Information Displayed:**  

- Volume of mug  
- On the second row, scrolling names of all selected users


??? tip "**Available Actions:**"
    - Press person button → Assign coffee to that person
    - Red button → Remove last assigned person, and if no one left, cancels and go back to base page
    - Encoder button → Confirm assignment to pre-selected users
    - Timeout → Same as encoder button **so no need to confirm on the encoder button**
