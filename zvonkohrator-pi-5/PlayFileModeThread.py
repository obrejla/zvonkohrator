from threading import Event, Lock, Thread

from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler
from PlayFileModeController import PlayFileModeController


class PlayFileModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        lock: Lock,
        should_stop_file_mode: Event,
        should_stop_keyboard_mode: Event,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
    ):
        super().__init__(daemon=True)
        self.lock = lock
        self.should_stop_file_mode = should_stop_file_mode
        self.should_stop_keyboard_mode = should_stop_keyboard_mode
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler

    def __show_init_message(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(0, 1)
        self.lcd.printout("Prehravani MIDI")

    def __run_file_mode(self):
        self.__show_init_message()
        play_file_mode_controller = PlayFileModeController(
            self.lcd, self.midi_note_on_handler
        )
        play_file_mode_controller.run(self.should_stop_file_mode)

    def run(self):
        print("wanna play file...")
        if not PlayFileModeThread.internal_lock.locked():
            PlayFileModeThread.internal_lock.acquire()
            self.should_stop_keyboard_mode.set()
            with self.lock:
                print("Lock acquired! Starting 'play file mode'...")
                self.should_stop_keyboard_mode.clear()
                self.__run_file_mode()
                self.should_stop_file_mode.clear()
                print("...ending 'play file mode'. Releasing lock.")
            PlayFileModeThread.internal_lock.release()
        else:
            print("but is already playing file :/")