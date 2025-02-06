from threading import Event, Lock, Thread
from time import sleep

from EnergyController import EnergyController
from KeyboardPlayerController import KeyboardPlayerController
from LCD import LCD
from MidiCommandHandlers import MidiCommandHandlers
from MidiListener import MidiListener
from MidiNoteOnHandler import MidiNoteOnHandler
from PlayerButtonsController import PlayerButtonsController


class PlayKeyboardModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        energy_controller: EnergyController,
        run_keyboard_mode: Event,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
        player_buttons_controller: PlayerButtonsController,
    ):
        super().__init__(daemon=True, name="PlayKeyboardModeThread")
        self.energy_controller = energy_controller
        self.run_keyboard_mode = run_keyboard_mode
        self.midi_note_on_handler = midi_note_on_handler
        self.lcd = lcd
        self.player_buttons_controller = player_buttons_controller
        midi_command_handlers = MidiCommandHandlers()
        midi_command_handlers.register(self.midi_note_on_handler)
        self.midi_listener = MidiListener(
            self.energy_controller, midi_command_handlers, lcd
        )
        self.keyboard_player_controller = KeyboardPlayerController(
            self.energy_controller,
            self.lcd,
            self.midi_note_on_handler,
            self.midi_listener,
            self.player_buttons_controller,
        )

    def __show_init_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(2, 1)
        self.lcd.printout("MIDI Keyboard")
        sleep(1)

    def __show_init_message(self):
        self.lcd.bulk_modify(self.__show_init_message_bulk)

    def __run_keyboard_mode(self):
        self.__show_init_message()
        self.keyboard_player_controller.run(self.run_keyboard_mode)

    def run(self):
        while True:
            if self.run_keyboard_mode.wait():
                print("wanna play keyboard...")
                acquired = PlayKeyboardModeThread.internal_lock.acquire(blocking=False)
                if acquired:
                    try:
                        print(
                            "PlayKeyboardModeThread lock acquired! Starting 'play keyboard mode'..."
                        )
                        t = Thread(
                            target=self.__run_keyboard_mode, name="KeyboardModeRunner"
                        )
                        t.start()
                        t.join()
                        print("...ending 'play keyboard mode'.")
                    finally:
                        print("Releasing PlayKeyboardModeThread lock.")
                        PlayKeyboardModeThread.internal_lock.release()
                else:
                    print("...but it is already playing keyboard :/")
