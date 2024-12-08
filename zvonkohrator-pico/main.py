import select
import sys

from machine import Pin

C2 = Pin(0, Pin.OUT)
Cis2 = Pin(1, Pin.OUT)
D2 = Pin(2, Pin.OUT)
Dis2 = Pin(3, Pin.OUT)
E2 = Pin(4, Pin.OUT)
F2 = Pin(5, Pin.OUT)
Fis2 = Pin(6, Pin.OUT)
G2 = Pin(7, Pin.OUT)
Gis2 = Pin(8, Pin.OUT)
A2 = Pin(9, Pin.OUT)
B2 = Pin(10, Pin.OUT)
H2 = Pin(11, Pin.OUT)
C3 = Pin(12, Pin.OUT)
Cis3 = Pin(13, Pin.OUT)
D3 = Pin(14, Pin.OUT)
Dis3 = Pin(15, Pin.OUT)
E3 = Pin(16, Pin.OUT)
F3 = Pin(17, Pin.OUT)
Fis3 = Pin(18, Pin.OUT)
G3 = Pin(19, Pin.OUT)
Gis3 = Pin(20, Pin.OUT)
A3 = Pin(21, Pin.OUT)
B3 = Pin(22, Pin.OUT)
H3 = Pin(26, Pin.OUT)
C4 = Pin(27, Pin.OUT)


def note_on(note: int):
    if note == 36:
        C2.on()
    elif note == 37:
        Cis2.on()
    elif note == 38:
        D2.on()
    elif note == 39:
        Dis2.on()
    elif note == 40:
        E2.on()
    elif note == 41:
        F2.on()
    elif note == 42:
        Fis2.on()
    elif note == 43:
        G2.on()
    elif note == 44:
        Gis2.on()
    elif note == 45:
        A2.on()
    elif note == 46:
        B2.on()
    elif note == 47:
        H2.on()
    elif note == 48:
        C3.on()
    elif note == 49:
        Cis3.on()
    elif note == 50:
        D3.on()
    elif note == 51:
        Dis3.on()
    elif note == 52:
        E3.on()
    elif note == 53:
        F3.on()
    elif note == 54:
        Fis3.on()
    elif note == 55:
        G3.on()
    elif note == 56:
        Gis3.on()
    elif note == 57:
        A3.on()
    elif note == 58:
        B3.on()
    elif note == 59:
        H3.on()
    elif note == 60:
        C4.on()


def note_off(note: int):
    if note == 36:
        C2.off()
    elif note == 37:
        Cis2.off()
    elif note == 38:
        D2.off()
    elif note == 39:
        Dis2.off()
    elif note == 40:
        E2.off()
    elif note == 41:
        F2.off()
    elif note == 42:
        Fis2.off()
    elif note == 43:
        G2.off()
    elif note == 44:
        Gis2.off()
    elif note == 45:
        A2.off()
    elif note == 46:
        B2.off()
    elif note == 47:
        H2.off()
    elif note == 48:
        C3.off()
    elif note == 49:
        Cis3.off()
    elif note == 50:
        D3.off()
    elif note == 51:
        Dis3.off()
    elif note == 52:
        E3.off()
    elif note == 53:
        F3.off()
    elif note == 54:
        Fis3.off()
    elif note == 55:
        G3.off()
    elif note == 56:
        Gis3.off()
    elif note == 57:
        A3.off()
    elif note == 58:
        B3.off()
    elif note == 59:
        H3.off()
    elif note == 60:
        C4.off()


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
            note_on(note)
        else:
            note_off(abs(note))
        continue
    else:
        # do something if no message received (like feed a watchdog timer)
        continue
