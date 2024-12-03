from serial import Serial


class MidiPlayer:
    def __init__(self, usb_port: str):
        self.serial = Serial(usb_port, 115200)

    def on_note_on(self, playable_tone: int):
        self.serial.write(f"{playable_tone}\r".encode())
        # response = self.serial.readline().strip()
        # print(response)

    def on_note_off(self, playable_tone: int):
        self.serial.write(f"{playable_tone * -1}\r".encode())
        # response = self.serial.readline().strip()
        # print(response)
