from serial import Serial


class MidiPlayer:
    def __init__(self, usb_port):
        self.serial = Serial(usb_port, 9600)

    def on_note_on(self, playable_tone):
        self.serial.write(f"{playable_tone}\r".encode())
        response = self.serial.readline().strip()
        print(response)

    def on_note_off(self, playable_tone):
        self.serial.write(f"{playable_tone}\r".encode())
        response = self.serial.readline().strip()
        print(response)
