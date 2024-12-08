from threading import Event, Lock, Thread
from time import sleep

from LCD import LCD
from MidiCommandHandlers import MidiCommandHandlers
from MidiListener import MidiListener
from MidiNoteOnHandler import MidiNoteOnHandler


class PlayKeyboardModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        run_keyboard_mode: Event,
        midi_note_on_handler: MidiNoteOnHandler,
        lcd: LCD,
    ):
        super().__init__(daemon=True, name="PlayKeyboardModeThread")
        self.run_keyboard_mode = run_keyboard_mode
        self.midi_note_on_handler = midi_note_on_handler
        self.lcd = lcd
        midi_command_handlers = MidiCommandHandlers()
        midi_command_handlers.register(self.midi_note_on_handler)
        self.midi_listener = MidiListener(midi_command_handlers)

    def __show_init_message(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(2, 1)
        self.lcd.printout("MIDI klavesy")

    def __run_keyboard_mode(self):
        self.__show_init_message()
        self.midi_listener.listen(self.run_keyboard_mode)

    def run(self):
        while True:
            sleep(1)
            if self.run_keyboard_mode.is_set():
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
