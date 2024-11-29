from machine import Pin, Timer
import select
import sys

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
        elif data == "48":
            C3.toggle()
        elif data == "49":
            Cis3.toggle()
        elif data == "50":
            D3.toggle()
        elif data == "51":
            Dis3.toggle()
        elif data == "52":
            E3.toggle()
        elif data == "53":
            F3.toggle()
        elif data == "54":
            Fis3.toggle()
        elif data == "55":
            G3.toggle()
        elif data == "56":
            Gis3.toggle()
        elif data == "57":
            A3.toggle()
        elif data == "58":
            B3.toggle()
        elif data == "59":
            H3.toggle()
        elif data == "60":
            C4.toggle()
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
