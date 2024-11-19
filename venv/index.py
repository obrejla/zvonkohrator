import time
import rtmidi


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


# from gpiozero import LED
class LED:
    def __init__(self, gpio_id):
        self.gpio_id = gpio_id

    def __str__(self):
        return f"{self.gpio_id}"


# _X __ __ channel
# 9_ __ __ note on
# 8_ __ __ note off
# __ 0X __ note number
# __ __ 0X velocity


gpio_C2 = LED(4)
gpio_Cis2 = LED(5)
gpio_D2 = LED(6)
gpio_Dis2 = LED(12)
gpio_E2 = LED(16)
gpio_F2 = LED(17)
gpio_Fis2 = LED(18)
gpio_G2 = LED(19)
gpio_Gis2 = LED(20)
gpio_A2 = LED(21)
gpio_B2 = LED(22)
gpio_H2 = LED(23)
gpio_C3 = LED(334)
gpio_Cis3 = LED(335)
gpio_D3 = LED(336)
gpio_Dis3 = LED(3312)
gpio_E3 = LED(3316)
gpio_F3 = LED(3317)
gpio_Fis3 = LED(3318)
gpio_G3 = LED(3319)
gpio_Gis3 = LED(3320)
gpio_A3 = LED(3321)
gpio_B3 = LED(3322)
gpio_H3 = LED(3323)
gpio_C4 = LED(444)

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
    C2: ("C2", gpio_C2),
    Cis2: ("Cis2", gpio_Cis2),
    D2: ("D2", gpio_D2),
    Dis2: ("Dis2", gpio_Dis2),
    E2: ("E2", gpio_E2),
    F2: ("F2", gpio_F2),
    Fis2: ("Fis2", gpio_Fis2),
    G2: ("G2", gpio_G2),
    Gis2: ("Gis2", gpio_Gis2),
    A2: ("A2", gpio_A2),
    B2: ("B2", gpio_B2),
    H2: ("H2", gpio_H2),
    C3: ("C3", gpio_C3),
    Cis3: ("Cis3", gpio_Cis3),
    D3: ("D3", gpio_D3),
    Dis3: ("Dis3", gpio_Dis3),
    E3: ("E3", gpio_E3),
    F3: ("F3", gpio_F3),
    Fis3: ("Fis3", gpio_Fis3),
    G3: ("G3", gpio_G3),
    Gis3: ("Gis3", gpio_Gis3),
    A3: ("A3", gpio_A3),
    B3: ("B3", gpio_B3),
    H3: ("H3", gpio_H3),
    C4: ("C4", gpio_C4),
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
    (playable_name, playable_gpio) = playable_tones[playable_tone]
    lcd.clear()
    lcd.setCursor(6, 0)
    lcd.printout(f"{playable_name}!")
    lcd.setCursor(2, 1)
    lcd.printout("...a necum!!")
    print(
        f"NOTE_ON:\nnote={note}\tplayable_tone={playable_tone}({playable_name})\tvelocity={velocity}\tgpio={playable_gpio}")


def note_off(note, velocity):
    playable_tone = find_playable_tone(note)
    (playable_name, playable_gpio) = playable_tones[playable_tone]
    print(
        f"NOTE_OFF:\nnote={note}\tplayable_tone={playable_tone}({playable_name})\tvelocity={velocity}\tgpio={playable_gpio}")


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
