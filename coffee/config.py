# Custom enter key (↵) to register into the LCD module
CUSTOM_CHARS = dict(
    enter = bytearray([0x10,0x10,0x10,0x14,0x12,0x1F,0x02,0x04])
)
CUSTOM_CHARS_IDX = {name: chr(idx) for (idx, name) in enumerate(CUSTOM_CHARS.keys())}

# When a mug is served, we can look in the past at which buttons were pressed to register the mug
# to the corresponding person(s). This variable holds the duration (in seconds) of this past interval 
# (starting from the moment the pot is removed from the machine).
# Set to None to disable this feature (then the button should always be pressed AFTER serving the mug)
MUG_BUTTON_LOOKBEHIND_DURATION = 15
