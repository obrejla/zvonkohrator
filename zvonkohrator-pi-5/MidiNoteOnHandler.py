from MidiCommandHandler import MidiCommandHandler
from abc import abstractmethod

class MidiNoteOnHandler(MidiCommandHandler):

    @abstractmethod
    def handle_note_on(self, note: int, velocity: int):
        pass
