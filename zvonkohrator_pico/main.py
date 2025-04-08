import select
import sys

from machine import Pin

NOTES_TO_PINS = {
    48: Pin(0, Pin.OUT),  # C2
    49: Pin(1, Pin.OUT),  # Cis2
    50: Pin(2, Pin.OUT),  # D2
    51: Pin(3, Pin.OUT),  # Dis2
    52: Pin(4, Pin.OUT),  # E2
    53: Pin(5, Pin.OUT),  # F2
    54: Pin(6, Pin.OUT),  # Fis2
    55: Pin(7, Pin.OUT),  # G2
    56: Pin(8, Pin.OUT),  # Gis2
    57: Pin(9, Pin.OUT),  # A2
    58: Pin(10, Pin.OUT),  # B2
    59: Pin(11, Pin.OUT),  # H2
    60: Pin(12, Pin.OUT),  # C3
    61: Pin(13, Pin.OUT),  # Cis3
    62: Pin(14, Pin.OUT),  # D3
    63: Pin(15, Pin.OUT),  # Dis3
    64: Pin(16, Pin.OUT),  # E3
    65: Pin(17, Pin.OUT),  # F3
    66: Pin(18, Pin.OUT),  # Fis3
    67: Pin(19, Pin.OUT),  # G3
    68: Pin(20, Pin.OUT),  # Gis3
    69: Pin(21, Pin.OUT),  # A3
    70: Pin(22, Pin.OUT),  # B3
    71: Pin(26, Pin.OUT),  # H3
    72: Pin(27, Pin.OUT),  # C4
}


def reset_all_notes():
    for note in NOTES_TO_PINS.values():
        note.off()


reset_all_notes()

# Set up the poll object
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

# Loop indefinitely
while True:
    try:
        # Wait for input on stdin
        poll_results = poll_obj.poll()  # the '1' is how long it will wait for message before looping again (in microseconds)
        if poll_results:
            # Read the data from stdin (read data coming from PC)
            data = sys.stdin.readline().strip()
            note = int(data)
            if note > 0:
                NOTES_TO_PINS[note].on()
            else:
                NOTES_TO_PINS[abs(note)].off()
            continue
        else:
            # do something if no message received (like feed a watchdog timer)
            continue
    except Exception:
        reset_all_notes()
