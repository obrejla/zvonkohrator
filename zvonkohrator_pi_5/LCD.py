from abc import ABC, abstractmethod


class LCD(ABC):
    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def set_cursor(self, col: int, row: int):
        pass

    @abstractmethod
    def printout(self, text: str):
        pass

    @abstractmethod
    def bulk_modify(self, callback):
        pass
