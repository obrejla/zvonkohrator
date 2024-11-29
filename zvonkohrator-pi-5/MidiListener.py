import rtmidi
import time
from MidiCommandHandler import MidiCommandHandler


class MidiListener:
    def __init__(self, command_handler: MidiCommandHandler):
        self.midi = MidiListener.connect_midi_device()
        self.command_handler = command_handler

    @staticmethod
    def connect_midi_device():
        midi_in = rtmidi.MidiIn()

        ports_dict = {k: v for (v, k) in enumerate(midi_in.get_ports())}

        print(f"Ports: {ports_dict}")

        midi_in.open_port(ports_dict["VMPK Output"])

        print(f"Is port open: {midi_in.is_port_open()}")
        print("Listening...")
        return midi_in

    def read_command(self):
        msg_and_dt = self.midi.get_message()
        if msg_and_dt:
            (msg, dt) = msg_and_dt  # dt - delay time is seconds

            command = hex(msg[0])
            self.command_handler.handle_command(command[2:3], msg[1], msg[2])
        else:
            time.sleep(0.001)

    def listen(self):
        try:
            while True:
                self.read_command()
        except KeyboardInterrupt:
            self.command_handler.clear()
