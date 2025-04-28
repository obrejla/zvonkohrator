from abc import ABC, abstractmethod


class LCD1602(ABC):
    @abstractmethod
    def command(self, cmd):
        pass

    @abstractmethod
    def write(self, data):
        pass

    @abstractmethod
    def setCursor(self, col, row):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def printout(self, arg):
        pass

    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def begin(self, cols, lines):
        pass
