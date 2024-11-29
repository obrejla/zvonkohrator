import time
import rtmidi
from serial import Serial

# USB hub - domaci
# ser = Serial("/dev/cu.usbmodem1201", 9600)
# USB hub - cestovni
ser = Serial("/dev/cu.usbmodem11101", 9600)


# from LCD1602 import LCD1602
class LCD1602:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows

    def clear(self):
        pass

    def setCursor(self, col, row):
        pass

    def printout(self, string):
        print(string)


# _X __ __ channel
# 9_ __ __ note on
# 8_ __ __ note off
# __ 0X __ note number
# __ __ 0X velocity

C2 = 36
Cis2 = 37
D2 = 38
Dis2 = 39
E2 = 40
F2 = 41
Fis2 = 42
G2 = 43
Gis2 = 44
A2 = 45
B2 = 46
H2 = 47
C3 = 48
Cis3 = 49
D3 = 50
Dis3 = 51
E3 = 52
F3 = 53
Fis3 = 54
G3 = 55
Gis3 = 56
A3 = 57
B3 = 58
H3 = 59
C4 = 60

octave = 12

playable_tones = {
    C2: "C2",
    Cis2: "Cis2",
    D2: "D2",
    Dis2: "Dis2",
    E2: "E2",
    F2: "F2",
    Fis2: "Fis2",
    G2: "G2",
    Gis2: "Gis2",
    A2: "A2",
    B2: "B2",
    H2: "H2",
    C3: "C3",
    Cis3: "Cis3",
    D3: "D3",
    Dis3: "Dis3",
    E3: "E3",
    F3: "F3",
    Fis3: "Fis3",
    G3: "G3",
    Gis3: "Gis3",
    A3: "A3",
    B3: "B3",
    H3: "H3",
    C4: "C4",
}


def find_lowest_similar(note):
    lowest_similar_note = note
    while lowest_similar_note < C2:
        lowest_similar_note += octave
    return lowest_similar_note


def find_highest_similar(note):
    highest_similar_note = note
    while highest_similar_note > C4:
        highest_similar_note -= octave
    return highest_similar_note


def find_playable_tone(note):
    if note < C2:
        return find_lowest_similar(note)
    elif note > C4:
        return find_highest_similar(note)
    return note


def note_on(note, velocity):
    playable_tone = find_playable_tone(note)
    playable_name = playable_tones[playable_tone]
    lcd.clear()
    lcd.setCursor(6, 0)
    lcd.printout(f"{playable_name}!")
    lcd.setCursor(2, 1)
    lcd.printout("...a necum!!")
    print(
        f"NOTE_ON:\nnote={note}\tplayable_tone={playable_tone}({playable_name})\tvelocity={velocity}")
    ser.write(f"{playable_tone}\r".encode())
    response = ser.readline().strip()
    print(response)


def note_off(note, velocity):
    playable_tone = find_playable_tone(note)
    playable_name = playable_tones[playable_tone]
    print(
        f"NOTE_OFF:\nnote={note}\tplayable_tone={playable_tone}({playable_name})\tvelocity={velocity}")
    ser.write(f"{playable_tone}\r".encode())
    response = ser.readline().strip()
    print(response)


def handle_command(cmd, note, velocity):
    note_on_byte = "9"
    note_off_byte = "8"
    if cmd == note_on_byte:
        note_on(note, velocity)
    elif cmd == note_off_byte:
        note_off(note, velocity)


def read_command(midi):
    msg_and_dt = midi.get_message()
    if msg_and_dt:
        (msg, dt) = msg_and_dt  # dt - delay time is seconds

        command = hex(msg[0])
        handle_command(command[2:3], msg[1], msg[2])
    else:
        time.sleep(0.001)


def connect_midi_device():
    midi_in = rtmidi.MidiIn()

    ports_dict = {k: v for (v, k) in enumerate(midi_in.get_ports())}

    print(f"Ports: {ports_dict}")

    midi_in.open_port(ports_dict["VMPK Output"])

    print(f"Is port open: {midi_in.is_port_open()}")
    print("Listening...")
    return midi_in


midi = connect_midi_device()
lcd = LCD1602(16, 2)
try:
    while True:
        read_command(midi)
except KeyboardInterrupt:
    lcd.clear()
    del lcd
# midi_out = rtmidi.MidiOut()
# midi_out.open_port(ports_dict["MIDI In"]);
#
# note_on = [0x92, 48, 100]
# note_off = [0x82, 48, 0]
#
# midi_out.send_message(note_on)
# time.sleep(1)
# midi_out.send_message(note_off)
