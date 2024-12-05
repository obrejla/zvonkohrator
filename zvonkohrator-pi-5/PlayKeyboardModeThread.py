from threading import Event, Lock, Thread
from MidiListener import MidiListener
from MidiCommandHandlers import MidiCommandHandlers
from MidiNoteOnHandlerImpl import MidiNoteOnHandlerImpl
from MidiPlayer import MidiPlayer
from LCD import LCD

class PlayKeyboardModeThread(Thread):

    internal_lock = Lock()

    def __init__(self, lock: Lock, should_stop_file_mode: Event, should_stop_keyboard_mode: Event, midi_player: MidiPlayer, lcd: LCD):
        super().__init__(daemon=True)
        self.lock = lock
        self.should_stop_file_mode = should_stop_file_mode
        self.should_stop_keyboard_mode = should_stop_keyboard_mode
        self.midi_player = midi_player
        self.lcd = lcd

    def __show_init_message(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(2, 1)
        self.lcd.printout("MIDI klavesy")

    def __run_keyboard_mode(self):
        self.__show_init_message()
        midi_note_on_handler = MidiNoteOnHandlerImpl(self.midi_player)
        midi_command_handlers = MidiCommandHandlers()
        midi_command_handlers.register(midi_note_on_handler)
        midi_listener = MidiListener(midi_command_handlers)
        midi_listener.listen(self.should_stop_keyboard_mode)

    def run(self):
        print("wanna play keyboard...")
        if not PlayKeyboardModeThread.internal_lock.locked():
            PlayKeyboardModeThread.internal_lock.acquire()
            self.should_stop_file_mode.set()
            with self.lock:
                print("Lock acquired! Starting 'play keyboard mode'...")
                self.should_stop_file_mode.clear()
                self.__run_keyboard_mode()
                self.should_stop_keyboard_mode.clear()
                print("...ending 'play keyboard mode'. Releasing lock.")
            PlayKeyboardModeThread.internal_lock.release()
        else:
            print("...but it is already playing keyboard :/")
