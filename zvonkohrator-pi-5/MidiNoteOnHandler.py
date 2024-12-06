from abc import abstractmethod

from MidiCommandHandler import MidiCommandHandler


class MidiNoteOnHandler(MidiCommandHandler):
    @abstractmethod
    def handle_note_on(self, note: int, velocity: int):
        pass
