from functools import partial
from threading import Thread

from gpiozero import LED, Button

from zvonkohrator_pi_5.EnergyController import EnergyController
from zvonkohrator_pi_5.TeamButtonsController import Team, TeamButtonsController
from zvonkohrator_pi_5.utils import throttle


class TeamButtonsControllerImpl(TeamButtonsController):
    def __init__(self, energy_controller: EnergyController):
        self.energy_controller = energy_controller
        self.red_team_button = Button(21)
        self.red_team_led = LED(25, active_high=False)
        self.green_team_button = Button(20)
        self.green_team_led = LED(8, active_high=False)
        self.blue_team_button = Button(16)
        self.blue_team_led = LED(7, active_high=False)
        self.yellow_team_button = Button(12)
        self.yellow_team_led = LED(1, active_high=False)

        self.clear_leds()

        throttle_red = throttle(lambda: self.__handle_pressed(Team.RED))
        throttle_green = throttle(lambda: self.__handle_pressed(Team.GREEN))
        throttle_blue = throttle(lambda: self.__handle_pressed(Team.BLUE))
        throttle_yellow = throttle(lambda: self.__handle_pressed(Team.YELLOW))

        self.red_team_button.when_pressed = throttle_red
        self.green_team_button.when_pressed = throttle_green
        self.blue_team_button.when_pressed = throttle_blue
        self.yellow_team_button.when_pressed = throttle_yellow

        self.on_pressed_listeners = []

    def turn_led_on(self, team_id: Team):
        if team_id == Team.RED:
            self.red_team_led.on()
        elif team_id == Team.GREEN:
            self.green_team_led.on()
        elif team_id == Team.BLUE:
            self.blue_team_led.on()
        elif team_id == Team.YELLOW:
            self.yellow_team_led.on()

    def clear_leds(self):
        self.red_team_led.off()
        self.green_team_led.off()
        self.blue_team_led.off()
        self.yellow_team_led.off()

    def add_on_pressed(self, on_pressed_listener):
        self.on_pressed_listeners.append(on_pressed_listener)

    def remove_on_pressed(self, on_pressed_listener):
        self.on_pressed_listeners.append(on_pressed_listener)

    def __handle_pressed(self, team_id: Team):
        print(f"Team {team_id} wants to process an action!")
        if self.energy_controller.is_energy_flowing():
            for listener in self.on_pressed_listeners:
                Thread(
                    target=partial(listener, team_id),
                    daemon=True,
                    name="HandleTeamButtonThread",
                ).start()
        else:
            print("...but energy does not flow :(")
