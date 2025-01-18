from threading import Thread

from gpiozero import LED, Button
from utils import throttle


class TeamButtonsController:
    def __init__(self):
        self.red_team_button = Button(21)
        self.red_team_led = LED(1)
        self.green_team_button = Button(20)
        self.green_team_led = LED(7)
        self.blue_team_button = Button(16)
        self.blue_team_led = LED(8)
        self.yellow_team_button = Button(12)
        self.yellow_team_led = LED(25)

        self.clear_leds()

        throttle_red = throttle(lambda: self.__handle_red())
        throttle_green = throttle(lambda: self.__handle_green())
        throttle_blue = throttle(lambda: self.__handle_blue())
        throttle_yellow = throttle(lambda: self.__handle_yellow())

        self.red_team_button.when_pressed = throttle_red
        self.green_team_button.when_pressed = throttle_green
        self.blue_team_button.when_pressed = throttle_blue
        self.yellow_team_button.when_pressed = throttle_yellow

        self.on_red_pressed_listeners = []
        self.on_green_pressed_listeners = []
        self.on_blue_pressed_listeners = []
        self.on_yellow_pressed_listeners = []

    def clear_leds(self):
        self.red_team_led.off()
        self.green_team_led.off()
        self.blue_team_led.off()
        self.yellow_team_led.off()

    def add_on_red_pressed(self, on_red_listener):
        self.on_red_pressed_listeners.append(on_red_listener)

    def remove_on_red_pressed(self, on_red_listener):
        self.on_red_pressed_listeners.remove(on_red_listener)

    def add_on_green_pressed(self, on_green_listener):
        self.on_green_pressed_listeners.append(on_green_listener)

    def remove_on_green_pressed(self, on_green_listener):
        self.on_green_pressed_listeners.remove(on_green_listener)

    def add_on_blue_pressed(self, on_blue_listener):
        self.on_blue_pressed_listeners.append(on_blue_listener)

    def remove_on_blue_pressed(self, on_blue_listener):
        self.on_blue_pressed_listeners.remove(on_blue_listener)

    def add_on_yellow_pressed(self, on_yellow_listener):
        self.on_yellow_pressed_listeners.append(on_yellow_listener)

    def remove_on_yellow_pressed(self, on_yellow_listener):
        self.on_yellow_pressed_listeners.remove(on_yellow_listener)

    def __handle_red(self):
        for red_listener in self.on_red_pressed_listeners:
            Thread(
                target=red_listener, daemon=True, name="HandleRedTeamButtonThread"
            ).start()

    def __handle_green(self):
        for green_listener in self.on_green_pressed_listeners:
            Thread(
                target=green_listener, daemon=True, name="HandleGreenTeamButtonThread"
            ).start()

    def __handle_blue(self):
        for blue_listener in self.on_blue_pressed_listeners:
            Thread(
                target=blue_listener,
                daemon=True,
                name="HandleBlueTeamButtonThread",
            ).start()

    def __handle_yellow(self):
        for yellow_listener in self.on_yellow_pressed_listeners:
            Thread(
                target=yellow_listener,
                daemon=True,
                name="HandleYellowButtonThread",
            ).start()
