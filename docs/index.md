# Coffee Machine Documentation

Welcome to the documentation for the Raspberry Pi-based coffee machine interface system! This project provides a comprehensive solution for managing a smart coffee machine with weight sensing, user interface, and coffee consumption tracking.

## What is this project?

This is an intelligent coffee machine interface built with Raspberry Pi that features:

- **Smart Weight Sensing**: Uses HX711 load cells to measure coffee weight and detect serving events
- **Interactive LCD Interface**: 16x2 LCD display with rotary encoder navigation
- **User Management**: Multiple user buttons for tracking individual coffee consumption  
- **Real-time Monitoring**: Continuous weight monitoring and automatic coffee serving detection
- **Data Logging**: Database storage of coffee consumption per user

## Key Features

- :material-scale: **Precision Scale Integration** - HX711-based weight measurement with noise filtering
- :material-monitor: **LCD User Interface** - Clear 16x2 display with custom characters and scrolling text
- :material-tune: **Rotary Encoder Navigation** - Smooth menu navigation and input handling
- :material-account-multiple: **Multi-User Support** - Individual buttons and consumption tracking per user
- :material-cog: **Hardware Abstraction** - Clean separation between hardware interfaces and application logic
- :material-database: **Data Persistence** - SQLite database for storing user preferences and consumption data

## How it Works

1. **Coffee Pot Detection**: The scale continuously monitors weight to detect when the coffee pot is removed
2. **Serving Detection**: When the pot is returned, weight increase indicates coffee was served to mugs
3. **User Assignment**: Users press their assigned buttons to claim served coffee
4. **Data Recording**: The system logs who drank coffee and how much

## Quick Navigation

=== "Getting Started"

    New to the project? Start here:
    
    - [Installation Guide](getting-started/installation.md) - Set up the software and dependencies
    - [Hardware Setup](getting-started/hardware-setup.md) - Wire up the Raspberry Pi components  
    - [Quick Start](getting-started/quick-start.md) - Get your coffee machine running

=== "Architecture"

    Understand how it works:
    
    - [System Overview](architecture/overview.md) - High-level architecture and design
    - [Components](architecture/components.md) - Detailed component documentation
    - [Data Flow](architecture/data-flow.md) - How data flows through the system

=== "API Reference"

    Code documentation:
    
    - [App Module](api/app.md) - Main application and page management
    - [IO Module](api/io.md) - Hardware interface components
    - [Configuration](api/config.md) - System configuration options

=== "User Guide"

    Using the system:
    
    - [Interface Guide](user-guide/interface.md) - How to navigate and use the LCD interface
    - [Calibration](user-guide/calibration.md) - Calibrating the scale and sensors
    - [Troubleshooting](user-guide/troubleshooting.md) - Common issues and solutions

## Project Structure

```
coffee/
├── coffee/                 # Main Python package
│   ├── app/               # Application logic and UI pages
│   ├── io/                # Hardware interface modules
│   └── config.py          # Configuration settings
├── scripts/               # Utility scripts and entry points
├── docs/                  # Documentation (this site!)
└── pyproject.toml         # Project configuration
```

## Getting Help

If you encounter issues or have questions:

1. Check the [Troubleshooting Guide](user-guide/troubleshooting.md)
2. Review the [API Reference](api/app.md) for technical details
3. Open an issue on [GitHub](https://github.com/Thomzoy/coffee/issues)

---

Ready to get started? Head to the [Installation Guide](getting-started/installation.md) to begin!