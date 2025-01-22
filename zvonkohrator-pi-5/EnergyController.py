from enum import Enum
from threading import Event

from gpiozero import Button


class Energy(Enum):
    FLOWS = "energy-flows"
    NONE = "no-energy"


class EnergyController:
    def __init__(self):
        self.energy_flows = Event()
        self.energy_button = Button(5)
        self.energy_flow_listeners = []

        self.energy_button.when_pressed = self.__energy_on
        self.energy_button.when_released = self.__energy_off

    def init(self):
        # handle state when Energy is already provided during the startup
        if self.energy_button.is_pressed:
            self.__energy_on()
        else:
            self.__energy_off()

    def __energy_on(self):
        self.energy_flows.set()
        print("Energy flows!")
        for listener in self.energy_flow_listeners:
            listener(Energy.FLOWS)

    def __energy_off(self):
        self.energy_flows.clear()
        print("...no energy :/")
        for listener in self.energy_flow_listeners:
            listener(Energy.NONE)

    def add_energy_flow_listener(self, listener):
        self.energy_flow_listeners.append(listener)

    def remove_energy_flow_listener(self, listener):
        self.energy_flow_listeners.remove(listener)

    def is_energy_flowing(self):
        return self.energy_flows.is_set()

    def wait_for_energy(self):
        return self.energy_flows.wait()
