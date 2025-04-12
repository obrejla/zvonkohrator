from os import listdir, path
from threading import Event, Lock
from time import sleep

from mido import MidiFile

from zvonkohrator_pi_5.EnergyController import Energy, EnergyController
from zvonkohrator_pi_5.LCD import LCD
from zvonkohrator_pi_5.MidiNoteOnHandler import MidiNoteOnHandler
from zvonkohrator_pi_5.midiutils import (
    extract_file_name,
    extract_note_on_messages_in_absolute_time,
    play_from_time_position,
)
from zvonkohrator_pi_5.PlayerButtonsController import PlayerButtonsController
from zvonkohrator_pi_5.utils import non_blocking_lock


class FilePlayerController:
    LOCAL_DIR_PATH = "./zvonkohrator_pi_5/midi-files"
    MEDIA_DIR_PATH = "/media/david"

    def __init__(
        self,
        energy_controller: EnergyController,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
        player_buttons_controller: PlayerButtonsController,
    ):
        self.energy_controller = energy_controller
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.player_buttons_controller = player_buttons_controller
        self.is_playing = Event()
        self.is_paused = Event()
        self.prev_next_lock = Lock()
        self.current_file_index = 0
        self.current_file_start_position = 0
        self.should_interrupt_playing = Event()
        self.should_pause = Event()
        self.file_paths = []
        self.on_finish_listeners = []
        self.on_play_listeners = []

    def add_on_finish_listener(self, listener):
        self.on_finish_listeners.append(listener)

    def remove_on_finish_listener(self, listener):
        self.on_finish_listeners.remove(listener)

    def __trigger_on_finish_listeners(self):
        for listener in self.on_finish_listeners:
            listener()

    def add_on_play_listener(self, listener):
        self.on_play_listeners.append(listener)

    def remove_on_play_listener(self, listener):
        self.on_play_listeners.remove(listener)

    def __trigger_on_play_listeners(self):
        for listener in self.on_play_listeners:
            listener()

    def __current_file_path(self):
        return self.file_paths[self.current_file_index]

    def __show_current_file_bulk(self):
        self.lcd.set_cursor(0, 1)
        self.lcd.printout(extract_file_name(self.__current_file_path()).ljust(16))
        self.lcd.set_cursor(11, 0)
        self.lcd.printout(
            f"{self.current_file_index + 1:02d}/{len(self.file_paths):02d}"
        )

    def __show_current_file(self):
        self.lcd.bulk_modify(self.__show_current_file_bulk)

    def __show_stopped_bulk(self):
        self.lcd.set_cursor(0, 0)
        self.lcd.printout("STOPPED!".ljust(11))

    def __show_stopped(self):
        self.lcd.bulk_modify(self.__show_stopped_bulk)

    def __show_playing_bulk(self):
        self.lcd.set_cursor(0, 0)
        self.lcd.printout("PLAYING!".ljust(11))

    def __show_playing(self):
        self.lcd.bulk_modify(self.__show_playing_bulk)

    def __show_paused_bulk(self):
        self.lcd.set_cursor(0, 0)
        self.lcd.printout("PAUSED!".ljust(11))

    def __show_paused(self):
        self.lcd.bulk_modify(self.__show_paused_bulk)

    def __show_init_display_bulk(self):
        self.lcd.clear()
        self.__show_stopped_bulk()
        self.__show_current_file_bulk()

    def __show_init_display(self):
        self.lcd.bulk_modify(self.__show_init_display_bulk)

    def __load_midi_files_from_dir(self, dir_path):
        print(f"Loading files from dir: {dir_path}")
        return [
            f"{dir_path}/{file_name}"
            for file_name in listdir(dir_path)
            if file_name.endswith(".mid") and not file_name.startswith(".")
        ]

    def __load_local_files(self):
        local_midi_files = self.__load_midi_files_from_dir(
            FilePlayerController.LOCAL_DIR_PATH
        )
        self.file_paths.extend(local_midi_files)

    def __load_usb_files(self):
        for item in listdir(FilePlayerController.MEDIA_DIR_PATH):
            potential_usb_dir = f"{FilePlayerController.MEDIA_DIR_PATH}/{item}"
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
                        self.__show_init_display()
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
            self.__show_current_file()
        elif self.is_paused.is_set():
            print("...which is PAUSED...")
            self.__show_stopped()
            self.is_paused.clear()
            self.current_file_start_position = 0
            self.__show_current_file()
        else:
            print("...but is already stopped.")

    def __handle_play_pause(self):
        if self.is_playing.is_set():
            self.handle_pause()
        else:
            self.__handle_play()

    def handle_pause(self):
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
            self.__trigger_on_play_listeners()

            self.__show_playing()
            self.__show_current_file()

            midi_file = MidiFile(self.__current_file_path())

            print(f"start_position={self.current_file_start_position}")
            extracted_messages = extract_note_on_messages_in_absolute_time(midi_file)
            current_file_position = play_from_time_position(
                extracted_messages,
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
            self.__trigger_on_finish_listeners()
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
                        self.__show_init_display()
                    else:
                        print("...playig started in the meantime of going to NEXT :/")
                else:
                    print("...lock for go NEXT was not acquired.")
        else:
            print("...but already playing (I'm in handle next)")

    def __handle_energy_flow_change(self, new_energy_state: Energy):
        if new_energy_state == Energy.NONE:
            self.__handle_stop()

    def run(self, run_mode: Event):
        self.player_buttons_controller.add_on_prev_pressed(self.__handle_prev)
        self.player_buttons_controller.add_on_stop_pressed(self.__handle_stop)
        self.player_buttons_controller.add_on_play_pause_pressed(
            self.__handle_play_pause
        )
        self.player_buttons_controller.add_on_next_pressed(self.__handle_next)

        self.energy_controller.add_energy_flow_listener(
            self.__handle_energy_flow_change
        )

        self.__load_files()
        self.__show_init_display()

        while run_mode.is_set():
            sleep(1)

        self.__handle_stop()
        while self.is_playing.is_set():
            sleep(0.3)

        self.current_file_start_position = 0

        self.player_buttons_controller.remove_on_prev_pressed(self.__handle_prev)
        self.player_buttons_controller.remove_on_stop_pressed(self.__handle_stop)
        self.player_buttons_controller.remove_on_play_pause_pressed(
            self.__handle_play_pause
        )
        self.player_buttons_controller.remove_on_next_pressed(self.__handle_next)

        self.energy_controller.remove_energy_flow_listener(
            self.__handle_energy_flow_change
        )
