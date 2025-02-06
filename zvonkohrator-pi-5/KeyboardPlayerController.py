from threading import Event, Lock
from time import sleep

from EnergyController import Energy, EnergyController
from KeyboardRecordNoteOnHandler import KeyboardRecordNoteOnHandler
from LCD import LCD
from MidiCommandHandlers import MidiCommandHandlers
from MidiListener import MidiListener
from MidiNoteOnHandler import MidiNoteOnHandler
from midiutils import (
    convert_recorded_messages_to_absolute_time,
    play_from_time_position,
)
from PlayerButtonsController import PlayerButtonsController
from utils import non_blocking_lock


class KeyboardPlayerController:
    TEAM_RECORDS_DIR_PATH = "./zvonkohrator-pi-5/team-records"

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

        self.current_record_handler = None
        self.midi_command_handlers = MidiCommandHandlers()
        self.midi_command_handlers.register(self.midi_note_on_handler)
        self.midi_listener = MidiListener(
            self.energy_controller, self.midi_command_handlers, lcd
        )

        self.modes = ("Pouze hrani...", "Cerveni", "Zeleni", "Modri", "Zluti")
        self.current_mode_index = 0
        self.current_file_start_position = 0
        self.prev_next_lock = Lock()
        self.is_playing = Event()
        self.is_paused = Event()
        self.is_recording = Event()
        self.should_pause = Event()
        self.should_interrupt_playing = Event()

    def __show_no_keyboard_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(1, 0)
        self.lcd.printout("CHYBA: KLAVESY")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout("NENALEZENY")

    def __show_no_keyboard_message(self):
        self.lcd.bulk_modify(self.__show_no_keyboard_message_bulk)

    def __show_mode_name_bulk(self):
        self.lcd.set_cursor(0, 1)
        self.lcd.printout(f"{self.modes[self.current_mode_index]}".ljust(16))

    def __show_current_mode_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)
        self.lcd.printout(
            f"Klavesy:     {self.current_mode_index + 1}/{len(self.modes)}"
        )
        if self.current_mode_index == 0:
            self.__show_mode_name_bulk()
        else:
            self.__show_stopped_bulk()

    def __show_current_mode(self):
        self.lcd.bulk_modify(self.__show_current_mode_bulk)

    def __show_recording_bulk(self):
        self.__show_mode_name_bulk()
        self.lcd.set_cursor(9, 1)
        self.lcd.printout("RECING!")

    def __show_recording(self):
        self.lcd.bulk_modify(self.__show_recording_bulk)

    def __show_playing_bulk(self):
        self.__show_mode_name_bulk()
        self.lcd.set_cursor(8, 1)
        self.lcd.printout("PLAYING!")

    def __show_playing(self):
        self.lcd.bulk_modify(self.__show_playing_bulk)

    def __show_stopped_bulk(self):
        self.__show_mode_name_bulk()
        self.lcd.set_cursor(8, 1)
        self.lcd.printout("STOPPED!")

    def __show_stopped(self):
        self.lcd.bulk_modify(self.__show_stopped_bulk)

    def __show_paused_bulk(self):
        self.__show_mode_name_bulk()
        self.lcd.set_cursor(9, 1)
        self.lcd.printout("PAUSED!")

    def __show_paused(self):
        self.lcd.bulk_modify(self.__show_paused_bulk)

    def __get_current_record_file_path(self):
        return f"{KeyboardPlayerController.TEAM_RECORDS_DIR_PATH}/{self.modes[self.current_mode_index].lower()}.zkht"

    def __handle_prev(self):
        print("Wanna go to prev keyboard mode...")
        if not self.is_playing.is_set() and not self.is_recording.is_set():
            with non_blocking_lock(self.prev_next_lock) as locked:
                if locked:
                    if not self.is_playing.is_set() and not self.is_recording.is_set():
                        self.current_mode_index = (
                            self.current_mode_index - 1
                            if self.current_mode_index > 0
                            else len(self.modes) - 1
                        )
                        print(f"current_mode={self.modes[self.current_mode_index]}")
                        self.__show_current_mode()
                    else:
                        print(
                            "...playing/recording started in the meantime of going to PREV :/"
                        )
                else:
                    print("...lock for go PREV was not acquired.")
        else:
            print("...but already playing/recording (I'm in handle prev)")

    def __handle_stop(self):
        print("Wanna STOP!")
        if self.is_playing.is_set():
            print("...when PLAYING...")
            self.should_interrupt_playing.set()
            self.__show_stopped()
        elif self.is_paused.is_set():
            print("...when PAUSED...")
            self.is_paused.clear()
            self.__show_stopped()
        elif self.is_recording.is_set():
            print("...when RECORDING...")
            self.is_recording.clear()
            self.__show_stopped()
            self.current_record_handler.write_to_file(
                self.__get_current_record_file_path()
            )
            self.midi_command_handlers.unregister(self.current_record_handler)
        else:
            print("...but is already stopped.")

    def __handle_play_pause(self):
        if not self.is_recording.is_set():
            if self.is_playing.is_set():
                self.__handle_pause()
            else:
                self.__handle_play()

    def __handle_pause(self):
        print("Wanna PAUSE!")
        if self.is_playing.is_set():
            self.should_pause.set()
            self.should_interrupt_playing.set()
        else:
            print("...but it is not PLAYING :/")

    def __handle_play(self):
        print("Wanna PLAY!")
        if not self.is_playing.is_set() and not self.is_recording.is_set():
            self.is_playing.set()
            self.is_paused.clear()
            self.should_interrupt_playing.clear()

            self.__show_playing()

            print(f"start_position={self.current_file_start_position}")
            extracted_messages = convert_recorded_messages_to_absolute_time(
                self.__get_current_record_file_path()
            )
            if len(extracted_messages) > 0:
                current_file_position = play_from_time_position(
                    extracted_messages,
                    self.midi_note_on_handler,
                    self.current_file_start_position,
                    self.should_interrupt_playing,
                )

            if self.should_interrupt_playing.is_set() and self.should_pause.is_set():
                self.__show_paused()
                self.current_file_start_position = current_file_position
                print("...current team record PAUSED.")
                self.is_paused.set()
            else:
                self.__show_stopped()
                self.current_file_start_position = 0
                print("...current team record STOPPED.")

            print(f"current_file_position={self.current_file_start_position}")
            self.is_playing.clear()
            self.should_pause.clear()
        else:
            print("...but it is already PLAYING/recording...")

    def __handle_next(self):
        print("Wanna go to next keyboard mode...")
        if not self.is_playing.is_set() and not self.is_recording.is_set():
            with non_blocking_lock(self.prev_next_lock) as locked:
                if locked:
                    if not self.is_playing.is_set() and not self.is_recording.is_set():
                        self.current_mode_index += 1
                        self.current_mode_index %= len(self.modes)
                        print(f"current_mode={self.modes[self.current_mode_index]}")
                        self.__show_current_mode()
                    else:
                        print(
                            "...playing/recording started in the meantime of going to NEXT :/"
                        )
                else:
                    print("...lock for go NEXT was not acquired.")
        else:
            print("...but already playing/recording (I'm in handle next)")

    def __handle_record(self):
        print("Wanna record!")
        if (
            self.current_mode_index > 0
            and not self.is_playing.is_set()
            and not self.is_recording.is_set()
        ):
            self.is_recording.set()
            self.__show_recording()
            self.current_record_handler = KeyboardRecordNoteOnHandler()
            self.midi_command_handlers.register(self.current_record_handler)
        else:
            print(
                f"...but already playing/recording/or in wrong mode - {self.modes[self.current_mode_index]} (I'm in handle record)"
            )

    def __handle_energy_flow_change(self, new_energy_state: Energy):
        if new_energy_state == Energy.NONE:
            self.__handle_stop()

    def run(self, run_mode: Event):
        if self.midi_listener.connect_midi_device():
            self.player_buttons_controller.add_on_prev_pressed(self.__handle_prev)
            self.player_buttons_controller.add_on_stop_pressed(self.__handle_stop)
            self.player_buttons_controller.add_on_play_pause_pressed(
                self.__handle_play_pause
            )
            self.player_buttons_controller.add_on_next_pressed(self.__handle_next)
            self.player_buttons_controller.add_on_record_pressed(self.__handle_record)

            self.energy_controller.add_energy_flow_listener(
                self.__handle_energy_flow_change
            )

            self.__show_current_mode()

            self.midi_listener.listen(run_mode)

            self.__handle_stop()
            while self.is_playing.is_set() or self.is_recording.is_set():
                sleep(0.3)

            self.current_file_start_position = 0
            self.current_mode_index = 0

            self.player_buttons_controller.remove_on_prev_pressed(self.__handle_prev)
            self.player_buttons_controller.remove_on_stop_pressed(self.__handle_stop)
            self.player_buttons_controller.remove_on_play_pause_pressed(
                self.__handle_play_pause
            )
            self.player_buttons_controller.remove_on_next_pressed(self.__handle_next)
            self.player_buttons_controller.remove_on_record_pressed(
                self.__handle_record
            )

            self.energy_controller.remove_energy_flow_listener(
                self.__handle_energy_flow_change
            )
        else:
            self.__show_no_keyboard_message()
            run_mode.clear()
