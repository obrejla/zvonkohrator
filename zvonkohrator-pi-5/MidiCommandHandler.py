from abc import ABC, abstractmethod


class MidiCommandHandler(ABC):
    @abstractmethod
    def handles(self, cmd: str):
        pass

    @abstractmethod
    def handle(self, msg, dt: int):
        pass
