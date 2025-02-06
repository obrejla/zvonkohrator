from threading import Event, Lock

from EnergyController import EnergyController
from LCD import LCD
from MidiListener import MidiListener
from MidiNoteOnHandler import MidiNoteOnHandler
from PlayerButtonsController import PlayerButtonsController
from utils import non_blocking_lock


class KeyboardPlayerController:
    def __init__(
        self,
        energy_controller: EnergyController,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
        midi_listener: MidiListener,
        player_buttons_controller: PlayerButtonsController,
    ):
        self.energy_controller = energy_controller
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.midi_listener = midi_listener
        self.player_buttons_controller = player_buttons_controller

        self.modes = ("Pouze hrani...", "Cerveni", "Zeleni", "Modri", "Zluti")
        self.current_mode_index = 0
        self.prev_next_lock = Lock()
        self.is_playing = Event()
        self.is_paused = Event()
        self.is_recording = Event()

    def __show_no_keyboard_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(1, 0)
        self.lcd.printout("CHYBA: KLAVESY")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout("NENALEZENY")

    def __show_no_keyboard_message(self):
        self.lcd.bulk_modify(self.__show_no_keyboard_message_bulk)

    def __show_current_mode_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)
        self.lcd.printout(
            f"Klavesy:     {self.current_mode_index + 1}/{len(self.modes)}"
        )
        self.lcd.set_cursor(0, 1)
        self.lcd.printout(f"{self.modes[self.current_mode_index]}".ljust(16))

    def __show_current_mode(self):
        self.lcd.bulk_modify(self.__show_current_mode_bulk)

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
        pass

    def __handle_play_pause(self):
        pass

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
        pass

    def run(self, run_keyboard_mode: Event):
        if self.midi_listener.connect_midi_device():
            self.player_buttons_controller.add_on_prev_pressed(self.__handle_prev)
            self.player_buttons_controller.add_on_stop_pressed(self.__handle_stop)
            self.player_buttons_controller.add_on_play_pause_pressed(
                self.__handle_play_pause
            )
            self.player_buttons_controller.add_on_next_pressed(self.__handle_next)
            self.player_buttons_controller.add_on_record_pressed(self.__handle_record)

            self.__show_current_mode()

            self.midi_listener.listen(run_keyboard_mode)

            self.player_buttons_controller.remove_on_prev_pressed(self.__handle_prev)
            self.player_buttons_controller.remove_on_stop_pressed(self.__handle_stop)
            self.player_buttons_controller.remove_on_play_pause_pressed(
                self.__handle_play_pause
            )
            self.player_buttons_controller.remove_on_next_pressed(self.__handle_next)
            self.player_buttons_controller.remove_on_record_pressed(
                self.__handle_record
            )
        else:
            self.__show_no_keyboard_message()
            run_keyboard_mode.clear()
