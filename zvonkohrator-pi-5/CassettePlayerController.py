import re
from os import listdir
from threading import Event, Lock
from time import sleep

from CassetteDetector import CassetteDetector
from EnergyController import Energy, EnergyController
from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler
from midiutils import play_from_time_position
from mido import MidiFile
from PlayerButtonsController import PlayerButtonsController


class CassettePlayerController:
    LOCAL_DIR_PATH = "./zvonkohrator-pi-5/cassette-files"
    FILE_CASSETTE_NUMBER_PATTERN = re.compile(r"^(\d{1,2})-.*")

    def __init__(
        self,
        energy_controller: EnergyController,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
        player_buttons_controller: PlayerButtonsController,
        cassette_detector: CassetteDetector,
    ):
        self.energy_controller = energy_controller
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.player_buttons_controller = player_buttons_controller
        self.cassette_detector = cassette_detector
        self.is_playing = Event()
        self.is_paused = Event()
        self.current_cassette_file_index = 0
        self.current_cassette_file_start_position = 0
        self.should_interrupt_playing = Event()
        self.should_pause = Event()
        self.file_paths = []
        self.lcd_lock = Lock()

    def __reset_file_paths(self):
        self.file_paths = ["" for _ in range(16)]

    def __load_midi_files_from_dir(self, dir_path):
        print(f"Loading cassette files from dir: {dir_path}")
        return [
            file_name
            for file_name in sorted(listdir(dir_path))
            if file_name.endswith(".mid") and not file_name.startswith(".")
        ]

    def __load_local_files(self):
        local_midi_files = self.__load_midi_files_from_dir(
            CassettePlayerController.LOCAL_DIR_PATH
        )
        for file_name in local_midi_files:
            matched_file_number = (
                CassettePlayerController.FILE_CASSETTE_NUMBER_PATTERN.match(file_name)
            )
            if matched_file_number is not None:
                cassette_number = int(matched_file_number.group(1))
                if cassette_number > 0 and cassette_number < 16:
                    self.file_paths[cassette_number] = (
                        f"{CassettePlayerController.LOCAL_DIR_PATH}/{file_name}"
                    )
                else:
                    print(f"Cassette number out of range! {cassette_number}")

    def __load_files(self):
        self.__reset_file_paths()
        self.__load_local_files()
        print(f"Cassettes paths: {self.file_paths}")

    def __show_loaded_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(4, 0)
        self.lcd.printout("LOADED!")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout(f"kazeta: {self.current_cassette_file_index}")

    def __show_loaded(self):
        self.lcd.bulk_modify(self.__show_loaded_bulk)

    def __show_not_available_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("Neexistuje!")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout(f"kazeta: {self.current_cassette_file_index}")

    def __show_not_available(self):
        self.lcd.bulk_modify(self.__show_not_available_bulk)

    def __show_insert_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(5, 0)
        self.lcd.printout("Vlozte")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout("kazetu...")

    def __show_insert(self):
        self.lcd.bulk_modify(self.__show_insert_bulk)

    def __is_selected_valid_cassette(self):
        return self.__current_file_path() != ""

    def __show_init_display(self):
        if self.current_cassette_file_index > 0:
            if self.__is_selected_valid_cassette():
                self.__show_loaded()
            else:
                self.__show_not_available()
        else:
            self.__show_insert()

    def __show_playing_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(4, 0)
        self.lcd.printout("PLAYING!")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout(f"kazeta: {self.current_cassette_file_index}")

    def __show_playing(self):
        self.lcd.bulk_modify(self.__show_playing_bulk)

    def __show_paused_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(4, 0)
        self.lcd.printout("PAUSED!")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout(f"kazeta: {self.current_cassette_file_index}")

    def __show_paused(self):
        self.lcd.bulk_modify(self.__show_paused_bulk)

    def __current_file_path(self):
        return self.file_paths[self.current_cassette_file_index]

    def __handle_cassette_change(self, new_cassette):
        if not self.is_playing.is_set() and not self.is_paused.is_set():
            self.current_cassette_file_index = new_cassette
            self.__show_init_display()

    def __handle_stop(self):
        print("Wanna STOP the cassette...")
        if self.is_playing.is_set():
            print("...which is PLAYING...")
            self.current_cassette_file_index = 0
            self.should_interrupt_playing.set()
        elif self.is_paused.is_set():
            print("...which is PAUSED...")
            self.current_cassette_file_index = 0
            self.__show_init_display()
            self.is_paused.clear()
            self.current_cassette_file_start_position = 0
        else:
            print("...but is already stopped.")

    def __handle_play_pause(self):
        if self.is_playing.is_set():
            self.__handle_pause()
        elif self.__is_selected_valid_cassette():
            self.__handle_play()

    def __handle_pause(self):
        print("Wanna PAUSE the cassette...")
        if self.is_playing.is_set():
            self.should_pause.set()
            self.should_interrupt_playing.set()
        else:
            print("...but it is not PLAYING :/")

    def __handle_play(self):
        print("Wanna PLAY the cassette...")
        if not self.is_playing.is_set():
            self.is_playing.set()
            self.is_paused.clear()
            self.should_interrupt_playing.clear()

            self.__show_playing()

            midi_file = MidiFile(self.__current_file_path())

            print(f"start_position={self.current_cassette_file_start_position}")
            current_file_position = play_from_time_position(
                midi_file,
                self.midi_note_on_handler,
                self.current_cassette_file_start_position,
                self.should_interrupt_playing,
            )

            if self.should_interrupt_playing.is_set() and self.should_pause.is_set():
                self.__show_paused()
                self.current_cassette_file_start_position = current_file_position
                print("...current cassette PAUSED.")
                self.is_paused.set()
            else:
                self.current_cassette_file_index = 0
                self.__show_init_display()
                self.current_cassette_file_start_position = 0
                print("...current cassette STOPPED.")

            print(
                f"current_cassette_file_position={self.current_cassette_file_start_position}"
            )
            self.is_playing.clear()
            self.should_pause.clear()
        else:
            print("...but it is already PLAYING...")

    def __handle_energy_flow_change(self, new_energy_state: Energy):
        if new_energy_state == Energy.NONE:
            self.__handle_stop()

    def run(self, run_cassette_mode: Event):
        self.player_buttons_controller.add_on_stop_pressed(self.__handle_stop)
        self.player_buttons_controller.add_on_play_pause_pressed(
            self.__handle_play_pause
        )

        self.cassette_detector.add_on_cassette_change(self.__handle_cassette_change)

        self.energy_controller.add_energy_flow_listener(
            self.__handle_energy_flow_change
        )

        self.__load_files()
        self.__show_init_display()

        while run_cassette_mode.is_set():
            sleep(1)

        self.__handle_stop()
        while self.is_playing.is_set():
            sleep(0.3)

        self.current_cassette_file_start_position = 0

        self.player_buttons_controller.remove_on_stop_pressed(self.__handle_stop)
        self.player_buttons_controller.remove_on_play_pause_pressed(
            self.__handle_play_pause
        )

        self.cassette_detector.remove_on_cassette_change(self.__handle_cassette_change)

        self.energy_controller.remove_energy_flow_listener(
            self.__handle_energy_flow_change
        )
