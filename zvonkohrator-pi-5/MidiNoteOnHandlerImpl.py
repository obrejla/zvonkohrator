from MidiNoteOnHandler import MidiNoteOnHandler
from MidiPlayer import MidiPlayer
from threading import Timer

# _X __ __ channel
# 9_ __ __ note on
# 8_ __ __ note off
# __ 0X __ note number
# __ __ 0X velocity

C2 = 36
Cis2 = 37
D2 = 38
Dis2 = 39
E2 = 40
F2 = 41
Fis2 = 42
G2 = 43
Gis2 = 44
A2 = 45
B2 = 46
H2 = 47
C3 = 48
Cis3 = 49
D3 = 50
Dis3 = 51
E3 = 52
F3 = 53
Fis3 = 54
G3 = 55
Gis3 = 56
A3 = 57
B3 = 58
H3 = 59
C4 = 60

OCTAVE = 12

PLAYABLE_TONES = {
    C2: "C2",
    Cis2: "Cis2",
    D2: "D2",
    Dis2: "Dis2",
    E2: "E2",
    F2: "F2",
    Fis2: "Fis2",
    G2: "G2",
    Gis2: "Gis2",
    A2: "A2",
    B2: "B2",
    H2: "H2",
    C3: "C3",
    Cis3: "Cis3",
    D3: "D3",
    Dis3: "Dis3",
    E3: "E3",
    F3: "F3",
    Fis3: "Fis3",
    G3: "G3",
    Gis3: "Gis3",
    A3: "A3",
    B3: "B3",
    H3: "H3",
    C4: "C4",
}

NOTE_ON_BYTE = "9"
NOTE_OFF_BYTE = "8"

# holy grail so the "cink" is the best
DEFAULT_NOTE_OFF_DELAY = 0.05

class MidiNoteOnHandlerImpl(MidiNoteOnHandler):
    def __init__(self, midi_player: MidiPlayer):
        self.midi_player = midi_player

    def handles(self, cmd: str):
        return cmd == NOTE_ON_BYTE

    def handle(self, msg, dt):
        self.handle_note_on(msg[1], msg[2])

    def handle_note_on(self, note: int, velocity: int):
        # note_on with velocity 0 means "note off"
        if velocity > 0:
            playable_tone = MidiNoteOnHandlerImpl.__find_playable_tone(note)
            playable_name = PLAYABLE_TONES[playable_tone]
            print(
                f"NOTE_ON:\nnote={note}\tplayable_tone={playable_tone}({playable_name})\tvelocity={velocity}")
            self.midi_player.on_note_on(playable_tone)
            self.__send_auto_note_off_after_delay(note)

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
        playable_name = PLAYABLE_TONES[playable_tone]
        print(
            f"NOTE_OFF:\nnote={note}\tplayable_tone={playable_tone}({playable_name})\tvelocity={velocity}")
        self.midi_player.on_note_off(playable_tone)
