from abc import abstractmethod

from zvonkohrator_pi_5.MidiCommandHandler import MidiCommandHandler


class MidiNoteOnHandler(MidiCommandHandler):
    @abstractmethod
    def handle_note_on(self, note: int, velocity: int):
        pass

    @abstractmethod
    def get_last_note(self):
        pass
