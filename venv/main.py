from machine import Pin, Timer
import select
import sys

C2 = Pin(4, Pin.OUT)
Cis2 = Pin(5, Pin.OUT)
D2 = Pin(6, Pin.OUT)
Dis2 = Pin(7, Pin.OUT)
E2 = Pin(8, Pin.OUT)
F2 = Pin(9, Pin.OUT)
Fis2 = Pin(10, Pin.OUT)
G2 = Pin(11, Pin.OUT)
Gis2 = Pin(12, Pin.OUT)
A2 = Pin(13, Pin.OUT)
B2 = Pin(14, Pin.OUT)
H2 = Pin(15, Pin.OUT)

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
        # data = sys.stdin.read(1)
        # Write the data to the input file
        print(data)
        # data2 = int(data)
        # print(data2)
        if data == "36":
            C2.toggle()
        elif data == "37":
            Cis2.toggle()
        elif data == "38":
            D2.toggle()
        elif data == "39":
            Dis2.toggle()
        elif data == "40":
            E2.toggle()
        elif data == "41":
            F2.toggle()
        elif data == "42":
            Fis2.toggle()
        elif data == "43":
            G2.toggle()
        elif data == "44":
            Gis2.toggle()
        elif data == "45":
            A2.toggle()
        elif data == "46":
            B2.toggle()
        elif data == "47":
            H2.toggle()
        continue
    else:
        # do something if no message received (like feed a watchdog timer)
        continue

#
# C2.toggle()
# Cis2.toggle()
# D2.toggle()
# Dis2.toggle()
# E2.toggle()
# F2.toggle()
# Fis2.toggle()
# G2.toggle()
# Gis2.toggle()
# A2.toggle()
# B2.toggle()
# H2.toggle()
