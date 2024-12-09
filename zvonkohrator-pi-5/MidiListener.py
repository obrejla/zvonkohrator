import time
from threading import Event

import rtmidi
from MidiCommandHandlers import MidiCommandHandlers


class MidiListener:
    def __init__(self, command_handlers: MidiCommandHandlers):
        self.midi = rtmidi.MidiIn()
        self.command_handlers = command_handlers

    def connect_midi_device(self):
        if not self.midi.is_port_open():
            ports_dict = {k: v for (v, k) in enumerate(self.midi.get_ports())}

            print(f"Ports: {ports_dict}")

            if "Minilab3:Minilab3 Minilab3 MIDI 24:0" in ports_dict:
                # Minilab3 keyboard
                self.midi.open_port(ports_dict["Minilab3:Minilab3 Minilab3 MIDI 24:0"])
            elif "VMPK Output:out 128:0" in ports_dict:
                # virtual midi keyboard on raspberry
                self.midi.open_port(ports_dict["VMPK Output:out 128:0"])
            elif "VMPK Output" in ports_dict:
                # virtual midi keyboard on mac
                self.midi.open_port(ports_dict["VMPK Output"])
            else:
                print("No available midi port!")

    def __read_command(self):
        msg_and_dt = self.midi.get_message()
        if msg_and_dt:
            (msg, dt) = msg_and_dt  # dt - delay time is seconds
            self.command_handlers.handle(msg, dt)
        else:
            time.sleep(0.001)

    def listen(self, run_keyboard_mode: Event):
        print("Listening...")
        while run_keyboard_mode.is_set():
            self.__read_command()
