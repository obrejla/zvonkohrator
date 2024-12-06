from threading import Event, Lock, Thread

from LCD import LCD
from MidiCommandHandlers import MidiCommandHandlers
from MidiListener import MidiListener
from MidiNoteOnHandler import MidiNoteOnHandler
from utils import non_blocking_lock


class PlayKeyboardModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        general_mode_lock: Lock,
        should_stop_file_mode: Event,
        should_stop_keyboard_mode: Event,
        midi_note_on_handler: MidiNoteOnHandler,
        lcd: LCD,
    ):
        super().__init__(daemon=True)
        self.general_mode_lock = general_mode_lock
        self.should_stop_file_mode = should_stop_file_mode
        self.should_stop_keyboard_mode = should_stop_keyboard_mode
        self.midi_note_on_handler = midi_note_on_handler
        self.lcd = lcd

    def __show_init_message(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(2, 1)
        self.lcd.printout("MIDI klavesy")

    def __run_keyboard_mode(self):
        self.__show_init_message()
        midi_command_handlers = MidiCommandHandlers()
        midi_command_handlers.register(self.midi_note_on_handler)
        midi_listener = MidiListener(midi_command_handlers)
        midi_listener.listen(self.should_stop_keyboard_mode)

    def run(self):
        print("wanna play keyboard...")
        with non_blocking_lock(PlayKeyboardModeThread.internal_lock) as locked:
            if locked:
                self.should_stop_file_mode.set()
                with self.general_mode_lock:
                    print("General lock acquired! Starting 'play keyboard mode'...")
                    self.should_stop_file_mode.clear()
                    self.__run_keyboard_mode()
                    self.should_stop_keyboard_mode.clear()
                    print("...ending 'play keyboard mode'. Releasing lock.")
            else:
                print("...but it is already playing keyboard :/")
