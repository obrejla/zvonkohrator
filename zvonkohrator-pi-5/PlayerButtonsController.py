from threading import Thread

from gpiozero import Button
from utils import throttle


class PlayerButtonsController:
    def __init__(self):
        self.prev_button = Button(26)
        self.stop_button = Button(19)
        self.play_pause_button = Button(13)
        self.next_button = Button(6)

        throttle_prev = throttle(lambda: self.__handle_prev())
        throttle_stop = throttle(lambda: self.__handle_stop())
        throttle_play_pause = throttle(lambda: self.__handle_play_pause())
        throttle_next = throttle(lambda: self.__handle_next())

        self.prev_button.when_pressed = throttle_prev
        self.stop_button.when_pressed = throttle_stop
        self.play_pause_button.when_pressed = throttle_play_pause
        self.next_button.when_pressed = throttle_next

        self.on_prev_pressed_listeners = []
        self.on_stop_pressed_listeners = []
        self.on_play_pause_pressed_listeners = []
        self.on_next_pressed_listeners = []

    def add_on_prev_pressed(self, on_prev_listener):
        self.on_prev_pressed_listeners.append(on_prev_listener)

    def add_on_stop_pressed(self, on_stop_listener):
        self.on_stop_pressed_listeners.append(on_stop_listener)

    def add_on_play_pause_pressed(self, on_play_pause_listener):
        self.on_play_pause_pressed_listeners.append(on_play_pause_listener)

    def add_on_next_pressed(self, on_next_listener):
        self.on_next_pressed_listeners.append(on_next_listener)

    def __handle_prev(self):
        for prev_listener in self.on_prev_pressed_listeners:
            Thread(
                target=prev_listener, daemon=True, name="HandlePrevButtonThread"
            ).start()

    def __handle_stop(self):
        for stop_listener in self.on_stop_pressed_listeners:
            Thread(
                target=stop_listener, daemon=True, name="HandleStopButtonThread"
            ).start()

    def __handle_play_pause(self):
        for play_pause_listener in self.on_play_pause_pressed_listeners:
            Thread(
                target=play_pause_listener,
                daemon=True,
                name="HandlePlayPauseButtonThread",
            ).start()

    def __handle_next(self):
        for next_listener in self.on_next_pressed_listeners:
            Thread(
                target=next_listener,
                daemon=True,
                name="HandleNextButtonThread",
            ).start()
