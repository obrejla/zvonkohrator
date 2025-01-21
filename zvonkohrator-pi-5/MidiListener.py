import time
from threading import Event

import rtmidi
from LCD import LCD
from MidiCommandHandlers import MidiCommandHandlers


class MidiListener:
    def __init__(
        self, energy_flows: Event, command_handlers: MidiCommandHandlers, lcd: LCD
    ):
        self.energy_flows = energy_flows
        self.midi = rtmidi.MidiIn()
        self.command_handlers = command_handlers
        self.lcd = lcd

    def connect_midi_device(self):
        if not self.midi.is_port_open():
            ports_dict = {k: v for (v, k) in enumerate(self.midi.get_ports())}

            print(f"Ports: {ports_dict}")

            for device_port in ports_dict:
                if device_port.startswith(
                    "Minilab3:Minilab3 Minilab3 MIDI"
                ) or device_port.startswith("VMPK Output"):
                    self.midi.open_port(ports_dict[device_port])
                    break

            if not self.midi.is_port_open():
                print("No available midi port!")
        return self.midi.is_port_open()

    def __read_command(self):
        msg_and_dt = self.midi.get_message()
        if msg_and_dt and self.energy_flows.is_set():
            (msg, dt) = msg_and_dt  # dt - delay time is seconds
            self.command_handlers.handle(msg, dt)
        else:
            time.sleep(0.001)

    def __display_init_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(4, 0)
        self.lcd.printout("Klavesy")
        self.lcd.set_cursor(2, 1)
        self.lcd.printout("pripojeny...")

    def __display_init_message(self):
        self.lcd.bulk_modify(self.__display_init_message_bulk)

    def listen(self, run_keyboard_mode: Event):
        self.__display_init_message()
        print("Listening...")
        while run_keyboard_mode.is_set():
            self.__read_command()
        self.midi.close_port()
        self.lcd.bulk_modify(self.lcd.clear)
