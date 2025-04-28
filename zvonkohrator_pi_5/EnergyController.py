from enum import Enum
from functools import partial
from threading import Event, Thread

from gpiozero import Button

from zvonkohrator_pi_5.utils import throttle


class Energy(Enum):
    FLOWS = "energy-flows"
    NONE = "no-energy"


class EnergyController:
    def __init__(self):
        self.energy_flows = Event()
        self.energy_button = Button(5)
        self.energy_flow_listeners = []

        throttled_energy_on = throttle(lambda: self.__energy_on())
        throttled_energy_off = throttle(lambda: self.__energy_off())

        self.energy_button.when_pressed = throttled_energy_on
        self.energy_button.when_released = throttled_energy_off

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
            Thread(
                target=partial(listener, Energy.FLOWS),
                daemon=True,
                name="HandleEnergyOnThread",
            ).start()

    def __energy_off(self):
        self.energy_flows.clear()
        print("...no energy :/")
        for listener in self.energy_flow_listeners:
            Thread(
                target=partial(listener, Energy.NONE),
                daemon=True,
                name="HandleEnergyOffThread",
            ).start()

    def add_energy_flow_listener(self, listener):
        self.energy_flow_listeners.append(listener)

    def remove_energy_flow_listener(self, listener):
        self.energy_flow_listeners.remove(listener)

    def is_energy_flowing(self):
        return self.energy_flows.is_set()

    def wait_for_energy(self):
        return self.energy_flows.wait()

    def start_bypass(self):
        self.energy_flows.set()

    def stop_bypass(self):
        if self.energy_button.is_pressed:
            self.__energy_on()
        else:
            self.__energy_off()
