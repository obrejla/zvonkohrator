import select
import sys

from machine import Pin

NOTES_TO_PINS = {
    36: Pin(0, Pin.OUT),  # C2
    37: Pin(1, Pin.OUT),  # Cis2
    38: Pin(2, Pin.OUT),  # D2
    39: Pin(3, Pin.OUT),  # Dis2
    40: Pin(4, Pin.OUT),  # E2
    41: Pin(5, Pin.OUT),  # F2
    42: Pin(6, Pin.OUT),  # Fis2
    43: Pin(7, Pin.OUT),  # G2
    44: Pin(8, Pin.OUT),  # Gis2
    45: Pin(9, Pin.OUT),  # A2
    46: Pin(10, Pin.OUT),  # B2
    47: Pin(11, Pin.OUT),  # H2
    48: Pin(12, Pin.OUT),  # C3
    49: Pin(13, Pin.OUT),  # Cis3
    50: Pin(14, Pin.OUT),  # D3
    51: Pin(15, Pin.OUT),  # Dis3
    52: Pin(16, Pin.OUT),  # E3
    53: Pin(17, Pin.OUT),  # F3
    54: Pin(18, Pin.OUT),  # Fis3
    55: Pin(19, Pin.OUT),  # G3
    56: Pin(20, Pin.OUT),  # Gis3
    57: Pin(21, Pin.OUT),  # A3
    58: Pin(22, Pin.OUT),  # B3
    59: Pin(26, Pin.OUT),  # H3
    60: Pin(27, Pin.OUT),  # C4
}

# Set up the poll object
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

# Loop indefinitely
while True:
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
