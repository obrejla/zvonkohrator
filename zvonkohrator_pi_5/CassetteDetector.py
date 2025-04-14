from gpiozero import Button

from zvonkohrator_pi_5.EnergyController import EnergyController


class CassetteDetector:
    def __init__(self, energy_controller: EnergyController):
        self.energy_controller = energy_controller
        self.one_button = Button(15)
        self.two_button = Button(18)
        self.three_button = Button(23)
        self.four_button = Button(24)
        self.on_cassette_change_listeners = []

        self.one = 0
        self.two = 0
        self.three = 0
        self.four = 0

        self.one_button.when_pressed = self.__set_one_on
        self.two_button.when_pressed = self.__set_two_on
        self.three_button.when_pressed = self.__set_three_on
        self.four_button.when_pressed = self.__set_four_on

        self.one_button.when_released = self.__set_one_off
        self.two_button.when_released = self.__set_two_off
        self.three_button.when_released = self.__set_three_off
        self.four_button.when_released = self.__set_four_off

    def __set_one_on(self):
        self.__set_one(1)

    def __set_one_off(self):
        self.__set_one(0)

    def __set_two_on(self):
        self.__set_two(1)

    def __set_two_off(self):
        self.__set_two(0)

    def __set_three_on(self):
        self.__set_three(1)

    def __set_three_off(self):
        self.__set_three(0)

    def __set_four_on(self):
        self.__set_four(1)

    def __set_four_off(self):
        self.__set_four(0)

    def __set_one(self, value: int):
        print(f"Someone wants to set cassette pin 1 to: {value}")
        if self.energy_controller.is_energy_flowing():
            self.one = value
            self.__handle_cassette_change()
        else:
            print("...but energy does not flow :(")

    def __set_two(self, value: int):
        print(f"Someone wants to set cassette pin 2 to: {value}")
        if self.energy_controller.is_energy_flowing():
            self.two = value
            self.__handle_cassette_change()
        else:
            print("...but energy does not flow :(")

    def __set_three(self, value: int):
        print(f"Someone wants to set cassette pin 3 to: {value}")
        if self.energy_controller.is_energy_flowing():
            self.three = value
            self.__handle_cassette_change()
        else:
            print("...but energy does not flow :(")

    def __set_four(self, value: int):
        print(f"Someone wants to set cassette pin 4 to: {value}")
        if self.energy_controller.is_energy_flowing():
            self.four = value
            self.__handle_cassette_change()
        else:
            print("...but energy does not flow :(")

    def add_on_cassette_change(self, listener):
        self.on_cassette_change_listeners.append(listener)

    def remove_on_cassette_change(self, listener):
        self.on_cassette_change_listeners.remove(listener)

    def __handle_cassette_change(self):
        new_cassette = int(f"{self.one}{self.two}{self.three}{self.four}", 2)
        print(
            f"New cassette detected: {new_cassette} - {self.one}{self.two}{self.three}{self.four}"
        )
        for listener in self.on_cassette_change_listeners:
            listener(new_cassette)
