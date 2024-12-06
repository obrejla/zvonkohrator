from signal import pause
from threading import Event, Thread

from gpiozero import Button
from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler
from midiutils import extract_file_name, play_from_time_position
from mido import MidiFile


class PlayFileModeController:
    def __init__(self, lcd: LCD, midi_note_on_handler: MidiNoteOnHandler):
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.prev_button = Button(26)
        self.stop_button = Button(19)
        self.play_pause_button = Button(13)
        self.next_button = Button(6)
        self.is_playing = Event()
        self.is_paused = Event()

    def __show_init_display(self):
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)
        self.lcd.printout("STOPPED!")
        self.lcd.set_cursor(10, 0)
        self.lcd.printout("01/05")
        self.lcd.set_cursor(0, 1)
        self.lcd.printout(extract_file_name(self.midi_file.filename))

    def __handle_prev(self):
        pass

    def __handle_stop(self):
        pass

    def __handle_play_pause(self):
        self.is_playing.set()
        self.is_paused.clear()

        self.lcd.set_cursor(0, 0)
        self.lcd.printout("PLAYING!")

        play_from_time_position(self.midi_file, self.midi_note_on_handler)

        self.lcd.set_cursor(0, 0)
        self.lcd.printout("STOPPED!")

        self.is_playing.clear()

    def __handle_next(self):
        pass

    def run(self, should_stop: Event):
        self.midi_file = MidiFile("./zvonkohrator-pi-5/midi-files/skakal-pes.mid")
        # TODO: handle should_stop when another game mode is requested
        self.should_stop = should_stop
        self.prev_button.when_pressed = lambda: Thread(
            target=self.__handle_prev, daemon=True
        ).start()
        self.stop_button.when_pressed = lambda: Thread(
            target=self.__handle_stop, daemon=True
        ).start()
        self.play_pause_button.when_pressed = lambda: Thread(
            target=self.__handle_play_pause, daemon=True
        ).start()
        self.next_button.when_pressed = lambda: Thread(
            target=self.__handle_next, daemon=True
        ).start()

        self.__show_init_display()

        pause()
