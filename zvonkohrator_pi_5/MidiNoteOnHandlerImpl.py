from threading import Timer

from zvonkohrator_pi_5.MidiCommandHandler import NOTE_ON_BYTE
from zvonkohrator_pi_5.MidiNoteOnHandler import MidiNoteOnHandler
from zvonkohrator_pi_5.MidiPlayer import MidiPlayer

# _X __ __ channel
# 9_ __ __ note on
# 8_ __ __ note off
# __ 0X __ note number
# __ __ 0X velocity

C2 = 48
Cis2 = 49
D2 = 50
Dis2 = 51
E2 = 52
F2 = 53
Fis2 = 54
G2 = 55
Gis2 = 56
A2 = 57
B2 = 58
H2 = 59
C3 = 60
Cis3 = 61
D3 = 62
Dis3 = 63
E3 = 64
F3 = 65
Fis3 = 66
G3 = 67
Gis3 = 68
A3 = 69
B3 = 70
H3 = 71
C4 = 72

OCTAVE = 12

# holy grail so the "cink" is the best
DEFAULT_NOTE_OFF_DELAY = 0.15

PLAYABLE_TONES = {
    C2: ("C2", DEFAULT_NOTE_OFF_DELAY),
    Cis2: ("Cis2", DEFAULT_NOTE_OFF_DELAY),
    D2: ("D2", DEFAULT_NOTE_OFF_DELAY),
    Dis2: ("Dis2", DEFAULT_NOTE_OFF_DELAY),
    E2: ("E2", DEFAULT_NOTE_OFF_DELAY),
    F2: ("F2", DEFAULT_NOTE_OFF_DELAY),
    Fis2: ("Fis2", DEFAULT_NOTE_OFF_DELAY),
    G2: ("G2", DEFAULT_NOTE_OFF_DELAY),
    Gis2: ("Gis2", DEFAULT_NOTE_OFF_DELAY),
    A2: ("A2", DEFAULT_NOTE_OFF_DELAY),
    B2: ("B2", DEFAULT_NOTE_OFF_DELAY),
    H2: ("H2", DEFAULT_NOTE_OFF_DELAY),
    C3: ("C3", DEFAULT_NOTE_OFF_DELAY),
    Cis3: ("Cis3", DEFAULT_NOTE_OFF_DELAY),
    D3: ("D3", DEFAULT_NOTE_OFF_DELAY),
    Dis3: ("Dis3", DEFAULT_NOTE_OFF_DELAY),
    E3: ("E3", DEFAULT_NOTE_OFF_DELAY),
    F3: ("F3", DEFAULT_NOTE_OFF_DELAY),
    Fis3: ("Fis3", DEFAULT_NOTE_OFF_DELAY),
    G3: ("G3", DEFAULT_NOTE_OFF_DELAY),
    Gis3: ("Gis3", DEFAULT_NOTE_OFF_DELAY),
    A3: ("A3", DEFAULT_NOTE_OFF_DELAY),
    B3: ("B3", DEFAULT_NOTE_OFF_DELAY),
    H3: ("H3", DEFAULT_NOTE_OFF_DELAY),
    C4: ("C4", DEFAULT_NOTE_OFF_DELAY),
}


class MidiNoteOnHandlerImpl(MidiNoteOnHandler):
    def __init__(self, midi_player: MidiPlayer):
        self.midi_player = midi_player
        self.last_note = 0
        self._debug = False

    def handles(self, cmd: str):
        return cmd[2:3] == NOTE_ON_BYTE

    def handle(self, msg, dt):
        self.handle_note_on(msg[1], msg[2])

    def get_last_note(self):
        return self.last_note

    def handle_note_on(self, note: int, velocity: int):
        # note_on with velocity 0 means "note off"
        if velocity > 0:
            playable_tone = MidiNoteOnHandlerImpl.__find_playable_tone(note)
            playable_tone_name = PLAYABLE_TONES[playable_tone][0]
            playable_tone_off_delay = PLAYABLE_TONES[playable_tone][1]
            if self._debug:
                print(
                    f"NOTE_ON:\nnote={note}\tplayable_tone={playable_tone}({playable_tone_name})\tvelocity={velocity}\toff_delay={playable_tone_off_delay}"
                )
            self.midi_player.on_note_on(playable_tone)
            self.last_note = note
            self.__send_auto_note_off_after_delay(note, playable_tone_off_delay)

    @staticmethod
    def __find_lowest_similar(note: int):
        lowest_similar_note = note
        while lowest_similar_note < C2:
            lowest_similar_note += OCTAVE
        return lowest_similar_note

    @staticmethod
    def __find_highest_similar(note: int):
        highest_similar_note = note
        while highest_similar_note > C4:
            highest_similar_note -= OCTAVE
        return highest_similar_note

    @staticmethod
    def __find_playable_tone(note: int):
        if note < C2:
            return MidiNoteOnHandlerImpl.__find_lowest_similar(note)
        elif note > C4:
            return MidiNoteOnHandlerImpl.__find_highest_similar(note)
        return note

    def __send_auto_note_off_after_delay(self, note: int, delay=DEFAULT_NOTE_OFF_DELAY):
        Timer(delay, self.__note_off, (note, 0)).start()

    def __note_off(self, note, velocity):
        playable_tone = MidiNoteOnHandlerImpl.__find_playable_tone(note)
        playable_tone_name = PLAYABLE_TONES[playable_tone][0]
        if self._debug:
            print(
                f"NOTE_OFF:\nnote={note}\tplayable_tone={playable_tone}({playable_tone_name})\tvelocity={velocity}"
            )
        self.midi_player.on_note_off(playable_tone)
