from threading import Event

from EnergyController import EnergyController
from LCD import LCD
from MidiListener import MidiListener
from MidiNoteOnHandler import MidiNoteOnHandler
from PlayerButtonsController import PlayerButtonsController


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

    def __show_no_keyboard_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(1, 0)
        self.lcd.printout("CHYBA: KLAVESY")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout("NENALEZENY")

    def __show_no_keyboard_message(self):
        self.lcd.bulk_modify(self.__show_no_keyboard_message_bulk)

    def __handle_prev(self):
        pass

    def __handle_stop(self):
        pass

    def __handle_play_pause(self):
        pass

    def __handle_next(self):
        pass

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

            self.midi_listener.listen(run_keyboard_mode)
        else:
            self.__show_no_keyboard_message()
            run_keyboard_mode.clear()
