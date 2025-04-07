from abc import ABC, abstractmethod

NOTE_ON_BYTE = "9"
NOTE_OFF_BYTE = "8"


class MidiCommandHandler(ABC):
    @abstractmethod
    def handles(self, cmd: str):
        pass

    @abstractmethod
    def handle(self, msg, dt: int):
        pass
