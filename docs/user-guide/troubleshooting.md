# Troubleshooting

Common issues and solutions for the coffee machine system.

* GPIO / Permission problems:
   * check that the `pigpiod` service is running (via `systemctl`)
   * check that the script is running as root
* Garbage text on LCD
   * happens when write instructions are incomplete (e.g. a thread stopping in the middle of the instruction)
   * to fix, turn off (small switch behind the board) the LCD, wait and turn on. If it doesn't work, turn off the Pi, then unplug and restart everything
* Strange behaviours
   * Be sure that a singe script is running (namely, not one via `systemd` and one that you ran yourself)

# Questions

* How to check the logs of the `coffee.service` (service launched at startup)
    * `sudo journalctl -u coffee.service`
