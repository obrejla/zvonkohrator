from signal import pause
from threading import Event, Lock, Thread
from time import sleep

from gpiozero import Button
from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler
from midiutils import extract_file_name, play_from_time_position
from mido import MidiFile
from utils import non_blocking_lock


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
        self.prev_next_lock = Lock()
        self.current_file_index = 0
        self.file_paths = (
            "./zvonkohrator-pi-5/midi-files/kocka-leze-dirou.mid",
            "./zvonkohrator-pi-5/midi-files/prsi-prsi.mid",
            "./zvonkohrator-pi-5/midi-files/skakal-pes.mid",
        )

    def __current_file_path(self):
        return self.file_paths[self.current_file_index]

    def __show_current_file(self):
        self.lcd.set_cursor(0, 1)
        self.lcd.printout(extract_file_name(self.__current_file_path()).ljust(16))
        self.lcd.set_cursor(10, 0)
        self.lcd.printout(
            f"{self.current_file_index + 1:02d}/{len(self.file_paths):02d}"
        )
        sleep(0.05)

    def __show_stopped(self):
        self.lcd.set_cursor(0, 0)
        self.lcd.printout("STOPPED!")

    def __show_playing(self):
        self.lcd.set_cursor(0, 0)
        self.lcd.printout("PLAYING!")

    def __show_init_display(self):
        self.lcd.clear()
        self.__show_stopped()
        self.__show_current_file()

    def __handle_prev(self):
        print("Wanna go to prev song...")
        if not self.is_playing.is_set():
            with non_blocking_lock(self.prev_next_lock) as locked:
                if locked:
                    if not self.is_playing.is_set():
                        self.current_file_index = (
                            self.current_file_index - 1
                            if self.current_file_index > 0
                            else len(self.file_paths) - 1
                        )
                        print(f"current_file={self.__current_file_path()}")
                        self.__show_current_file()
                        # sleep for a while so the processing takes a bit more time so the potential another "trigger" of button pressed event does not pass
                        sleep(0.3)
                    else:
                        print("...playig started in the meantime of going to PREV :/")
                else:
                    print("...lock for go NEXT was not acquired.")
        else:
            print("...but already playing (I'm in handle prev)")

    def __handle_stop(self):
        pass

    def __handle_play_pause(self):
        self.is_playing.set()
        self.is_paused.clear()

        self.__show_playing()

        midi_file = MidiFile(self.__current_file_path())

        play_from_time_position(midi_file, self.midi_note_on_handler)

        self.__show_stopped()

        self.is_playing.clear()

    def __handle_next(self):
        print("Wanna go to next song...")
        if not self.is_playing.is_set():
            with non_blocking_lock(self.prev_next_lock) as locked:
                if locked:
                    if not self.is_playing.is_set():
                        self.current_file_index += 1
                        self.current_file_index %= len(self.file_paths)
                        print(f"current_file={self.__current_file_path()}")
                        self.__show_current_file()
                        # sleep for a while so the processing takes a bit more time so the potential another "trigger" of button pressed event does not pass
                        sleep(0.3)
                    else:
                        print("...playig started in the meantime of going to NEXT :/")
                else:
                    print("...lock for go NEXT was not acquired.")
        else:
            print("...but already playing (I'm in handle next)")

    def run(self, should_stop: Event):
        # TODO: handle should_stop when another game mode is requested
        self.should_stop = should_stop
        self.prev_button.when_pressed = lambda: Thread(
            target=self.__handle_prev, daemon=True, name="HandlePrevButtonThread"
        ).start()
        self.stop_button.when_pressed = lambda: Thread(
            target=self.__handle_stop, daemon=True, name="HandleStopButtonThread"
        ).start()
        self.play_pause_button.when_pressed = lambda: Thread(
            target=self.__handle_play_pause,
            daemon=True,
            name="HandlePlayPauseButtonThread",
        ).start()
        self.next_button.when_pressed = lambda: Thread(
            target=self.__handle_next, daemon=True, name="HandleNextButtonThread"
        ).start()

        self.__show_init_display()

        pause()
