import rtmidi
import time
from MidiCommandHandlers import MidiCommandHandlers
from threading import Event


class MidiListener:
    def __init__(self, command_handlers: MidiCommandHandlers):
        self.midi = MidiListener.connect_midi_device()
        self.command_handlers = command_handlers

    @staticmethod
    def connect_midi_device():
        midi_in = rtmidi.MidiIn()

        ports_dict = {k: v for (v, k) in enumerate(midi_in.get_ports())}

        print(f"Ports: {ports_dict}")

        # virtual midi keyboard on raspberry
        midi_in.open_port(ports_dict["VMPK Output:out 128:0"])
        # virtual midi keyboard on mac
        # midi_in.open_port(ports_dict["VMPK Output"])

        print(f"Is port open: {midi_in.is_port_open()}")
        print("Listening...")
        return midi_in

    def read_command(self):
        msg_and_dt = self.midi.get_message()
        if msg_and_dt:
            (msg, dt) = msg_and_dt  # dt - delay time is seconds
            self.command_handlers.handle(msg, dt)
        else:
            time.sleep(0.001)

    def listen(self, should_stop: Event):
        while True and not should_stop.is_set():
            self.read_command()
