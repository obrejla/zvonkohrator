from abc import ABC, abstractmethod
from enum import Enum


class Team(Enum):
    RED = "Ce"
    GREEN = "Ze"
    BLUE = "Mo"
    YELLOW = "Zl"


class TeamButtonsController(ABC):
    @abstractmethod
    def clear_leds(self):
        pass

    @abstractmethod
    def turn_led_on(self, team_id: Team):
        pass

    @abstractmethod
    def add_on_pressed(self, on_pressed_listener):
        pass

    @abstractmethod
    def remove_on_pressed(self, on_pressed_listener):
        pass
