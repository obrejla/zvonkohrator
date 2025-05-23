import time
from threading import Event

import rtmidi

from zvonkohrator_pi_5.EnergyController import EnergyController
from zvonkohrator_pi_5.LCD import LCD
from zvonkohrator_pi_5.MidiCommandHandlers import MidiCommandHandlers


class MidiListener:
    def __init__(
        self,
        energy_controller: EnergyController,
        command_handlers: MidiCommandHandlers,
        lcd: LCD,
    ):
        self.energy_controller = energy_controller
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
        if msg_and_dt and self.energy_controller.is_energy_flowing():
            (msg, dt) = msg_and_dt  # dt - delay time is seconds
            self.command_handlers.handle(msg, dt)
        else:
            time.sleep(0.001)

    def listen(self, run_keyboard_mode: Event):
        print("Listening...")
        while run_keyboard_mode.is_set():
            self.__read_command()
        self.midi.close_port()
