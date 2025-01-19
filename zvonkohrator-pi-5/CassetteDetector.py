from threading import Thread

from gpiozero import Button


class CassetteDetector:
    def __init__(self):
        self.one_button = Button(15)
        self.two_button = Button(18)
        self.three_button = Button(23)
        self.four_button = Button(24)
        self.on_cassette_change_listeners = []

        self.one = 0
        self.two = 0
        self.three = 0
        self.four = 0

        self.one_button.when_pressed = lambda: Thread(
            target=lambda: self.__set_one(1),
            daemon=True,
            name="HandleCassetteButtonOneOn",
        ).start()
        self.two_button.when_pressed = lambda: Thread(
            target=lambda: self.__set_two(1),
            daemon=True,
            name="HandleCassetteButtonTwoOn",
        ).start()
        self.three_button.when_pressed = lambda: Thread(
            target=lambda: self.__set_three(1),
            daemon=True,
            name="HandleCassetteButtonThreeOn",
        ).start()
        self.four_button.when_pressed = lambda: Thread(
            target=lambda: self.__set_four(1),
            daemon=True,
            name="HandleCassetteButtonFourOn",
        ).start()

        self.one_button.when_released = lambda: Thread(
            target=lambda: self.__set_one(0),
            daemon=True,
            name="HandleCassetteButtonOneOff",
        ).start()
        self.two_button.when_released = lambda: Thread(
            target=lambda: self.__set_two(0),
            daemon=True,
            name="HandleCassetteButtonTwoOff",
        ).start()
        self.three_button.when_released = lambda: Thread(
            target=lambda: self.__set_three(0),
            daemon=True,
            name="HandleCassetteButtonThreeOff",
        ).start()
        self.four_button.when_released = lambda: Thread(
            target=lambda: self.__set_four(0),
            daemon=True,
            name="HandleCassetteButtonFourOff",
        ).start()

    def __set_one(self, value: int):
        self.one = value
        self.__handle_cassette_change()

    def __set_two(self, value: int):
        self.two = value
        self.__handle_cassette_change()

    def __set_three(self, value: int):
        self.three = value
        self.__handle_cassette_change()

    def __set_four(self, value: int):
        self.four = value
        self.__handle_cassette_change()

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
