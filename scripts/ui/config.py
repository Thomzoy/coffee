CUSTOM_CHARS = dict(
    enter = bytearray([0x10,0x10,0x10,0x14,0x12,0x1F,0x02,0x04])
)
CUSTOM_CHARS_IDX = {name: chr(idx) for (idx, name) in enumerate(CUSTOM_CHARS.keys())}
