from threading import Thread

from gpiozero import Button

from zvonkohrator_pi_5.EnergyController import EnergyController
from zvonkohrator_pi_5.RemoteController import RemoteController
from zvonkohrator_pi_5.utils import throttle


class PlayerButtonsController:
    def __init__(
        self, energy_controller: EnergyController, remote_controller: RemoteController
    ):
        self.energy_controller = energy_controller
        self.prev_button = Button(26)
        self.stop_button = Button(19, hold_time=2)
        self.play_pause_button = Button(13)
        self.next_button = Button(6)

        throttle_prev = throttle(lambda: self.__handle_prev())
        throttle_stop = throttle(lambda: self.__handle_stop())
        throttle_play_pause = throttle(lambda: self.__handle_play_pause())
        throttle_next = throttle(lambda: self.__handle_next())
        throttle_record = throttle(lambda: self.__handle_record())

        self.prev_button.when_pressed = throttle_prev
        self.stop_button.when_pressed = throttle_stop
        self.play_pause_button.when_pressed = throttle_play_pause
        self.next_button.when_pressed = throttle_next
        self.stop_button.when_held = throttle_record
        remote_controller.prev_buton.when_pressed = throttle_prev
        remote_controller.stop_button.when_pressed = throttle_stop
        remote_controller.play_pause_button.when_pressed = throttle_play_pause
        remote_controller.next_button.when_pressed = throttle_next

        self.on_prev_pressed_listeners = []
        self.on_stop_pressed_listeners = []
        self.on_play_pause_pressed_listeners = []
        self.on_next_pressed_listeners = []
        self.on_record_pressed_listeners = []

    def add_on_prev_pressed(self, on_prev_listener):
        self.on_prev_pressed_listeners.append(on_prev_listener)

    def remove_on_prev_pressed(self, on_prev_listener):
        self.on_prev_pressed_listeners.remove(on_prev_listener)

    def add_on_stop_pressed(self, on_stop_listener):
        self.on_stop_pressed_listeners.append(on_stop_listener)

    def remove_on_stop_pressed(self, on_stop_listener):
        self.on_stop_pressed_listeners.remove(on_stop_listener)

    def add_on_play_pause_pressed(self, on_play_pause_listener):
        self.on_play_pause_pressed_listeners.append(on_play_pause_listener)

    def remove_on_play_pause_pressed(self, on_play_pause_listener):
        self.on_play_pause_pressed_listeners.remove(on_play_pause_listener)

    def add_on_next_pressed(self, on_next_listener):
        self.on_next_pressed_listeners.append(on_next_listener)

    def remove_on_next_pressed(self, on_next_listener):
        self.on_next_pressed_listeners.remove(on_next_listener)

    def add_on_record_pressed(self, on_record_listener):
        self.on_record_pressed_listeners.append(on_record_listener)

    def remove_on_record_pressed(self, on_record_listener):
        self.on_record_pressed_listeners.remove(on_record_listener)

    def __handle_prev(self):
        print("Someone wants to trigger 'prev' action!")
        if self.energy_controller.is_energy_flowing():
            for prev_listener in self.on_prev_pressed_listeners:
                Thread(
                    target=prev_listener, daemon=True, name="HandlePrevButtonThread"
                ).start()
        else:
            print("...but energy does not flow :(")

    def __handle_stop(self):
        print("Someone wants to trigger 'stop' action!")
        if self.energy_controller.is_energy_flowing():
            for stop_listener in self.on_stop_pressed_listeners:
                Thread(
                    target=stop_listener, daemon=True, name="HandleStopButtonThread"
                ).start()
        else:
            print("...but energy does not flow :(")

    def __handle_play_pause(self):
        print("Someone wants to trigger 'play/pause' action!")
        if self.energy_controller.is_energy_flowing():
            for play_pause_listener in self.on_play_pause_pressed_listeners:
                Thread(
                    target=play_pause_listener,
                    daemon=True,
                    name="HandlePlayPauseButtonThread",
                ).start()
        else:
            print("...but energy does not flow :(")

    def __handle_next(self):
        print("Someone wants to trigger 'next' action!")
        if self.energy_controller.is_energy_flowing():
            for next_listener in self.on_next_pressed_listeners:
                Thread(
                    target=next_listener,
                    daemon=True,
                    name="HandleNextButtonThread",
                ).start()
        else:
            print("...but energy does not flow :(")

    def __handle_record(self):
        print("Someone wants to trigger 'record' action!")
        if self.energy_controller.is_energy_flowing():
            for record_listener in self.on_record_pressed_listeners:
                Thread(
                    target=record_listener, daemon=True, name="HandleRecordButtonThread"
                ).start()
        else:
            print("...but energy does not flow :(")
