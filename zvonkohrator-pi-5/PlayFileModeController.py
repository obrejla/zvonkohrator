from os import listdir, path
from threading import Event, Lock, Thread
from time import sleep

from gpiozero import Button
from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler
from midiutils import extract_file_name, play_from_time_position
from mido import MidiFile
from utils import non_blocking_lock, throttle


class PlayFileModeController:
    LOCAL_DIR_PATH = "./zvonkohrator-pi-5/midi-files"
    MEDIA_DIR_PATH = "/media/david"

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
        self.current_file_start_position = 0
        self.should_interrupt_playing = Event()
        self.should_pause = Event()
        self.file_paths = []

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
        self.lcd.printout("STOPPED!".ljust(11))

    def __show_playing(self):
        self.lcd.set_cursor(0, 0)
        self.lcd.printout("PLAYING!".ljust(11))

    def __show_paused(self):
        self.lcd.set_cursor(0, 0)
        self.lcd.printout("PAUSED!".ljust(11))

    def __show_init_display(self):
        self.lcd.clear()
        self.__show_stopped()
        self.__show_current_file()

    def __load_midi_files_from_dir(self, dir_path):
        print(f"Loading files from dir: {dir_path}")
        return [
            f"{dir_path}/{file_name}"
            for file_name in listdir(dir_path)
            if file_name.endswith(".mid")
        ]

    def __load_local_files(self):
        local_midi_files = self.__load_midi_files_from_dir(
            PlayFileModeController.LOCAL_DIR_PATH
        )
        self.file_paths.extend(local_midi_files)

    def __load_usb_files(self):
        for item in listdir(PlayFileModeController.MEDIA_DIR_PATH):
            potential_usb_dir = f"{PlayFileModeController.MEDIA_DIR_PATH}/{item}"
            if path.isdir(potential_usb_dir):
                print(f"Checking media: {potential_usb_dir}...")
                usb_files = self.__load_midi_files_from_dir(potential_usb_dir)
                self.file_paths.extend(usb_files)
            else:
                print(f"Not a directory: {item}")

    def __load_files(self):
        self.file_paths.clear()
        self.__load_local_files()
        self.__load_usb_files()

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
                    else:
                        print("...playig started in the meantime of going to PREV :/")
                else:
                    print("...lock for go NEXT was not acquired.")
        else:
            print("...but already playing (I'm in handle prev)")

    def __handle_stop(self):
        print("Wanna STOP the song...")
        if self.is_playing.is_set():
            print("...which is PLAYING...")
            self.should_interrupt_playing.set()
        elif self.is_paused.is_set():
            print("...which is PAUSED...")
            self.__show_stopped()
            self.is_paused.clear()
            self.current_file_start_position = 0
        else:
            print("...but is already stopped.")

    def __handle_play_pause(self):
        if self.is_playing.is_set():
            self.__handle_pause()
        else:
            self.__handle_play()

    def __handle_pause(self):
        print("Wanna PAUSE the song...")
        if self.is_playing.is_set():
            self.should_pause.set()
            self.should_interrupt_playing.set()
        else:
            print("...but it is not PLAYING :/")

    def __handle_play(self):
        print("Wanna PLAY the song...")
        if not self.is_playing.is_set():
            self.is_playing.set()
            self.is_paused.clear()
            self.should_interrupt_playing.clear()

            self.__show_playing()

            midi_file = MidiFile(self.__current_file_path())

            print(f"start_position={self.current_file_start_position}")
            current_file_position = play_from_time_position(
                midi_file,
                self.midi_note_on_handler,
                self.current_file_start_position,
                self.should_interrupt_playing,
            )

            if self.should_interrupt_playing.is_set() and self.should_pause.is_set():
                self.__show_paused()
                self.current_file_start_position = current_file_position
                print("...current file PAUSED.")
                self.is_paused.set()
            else:
                self.__show_stopped()
                self.current_file_start_position = 0
                print("...current file STOPPED.")

            print(f"current_file_position={self.current_file_start_position}")
            self.is_playing.clear()
            self.should_pause.clear()
        else:
            print("...but it is already PLAYING...")

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
                    else:
                        print("...playig started in the meantime of going to NEXT :/")
                else:
                    print("...lock for go NEXT was not acquired.")
        else:
            print("...but already playing (I'm in handle next)")

    def run(self, run_file_mode: Event):
        throttle_prev = throttle(
            lambda: Thread(
                target=self.__handle_prev, daemon=True, name="HandlePrevButtonThread"
            ).start()
        )
        throttle_stop = throttle(
            lambda: Thread(
                target=self.__handle_stop, daemon=True, name="HandleStopButtonThread"
            ).start()
        )
        throttle_play_pause = throttle(
            lambda: Thread(
                target=self.__handle_play_pause,
                daemon=True,
                name="HandlePlayPauseButtonThread",
            ).start()
        )
        throttle_next = throttle(
            lambda: Thread(
                target=self.__handle_next, daemon=True, name="HandleNextButtonThread"
            ).start()
        )

        self.prev_button.when_pressed = throttle_prev
        self.stop_button.when_pressed = throttle_stop
        self.play_pause_button.when_pressed = throttle_play_pause
        self.next_button.when_pressed = throttle_next

        self.__load_files()
        self.__show_init_display()

        while run_file_mode.is_set():
            sleep(1)

        self.__handle_stop()
        while self.is_playing.is_set():
            sleep(0.3)

        self.current_file_start_position = 0
