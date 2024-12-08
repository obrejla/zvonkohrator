from threading import Event, Lock, Thread
from time import sleep

from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler
from PlayFileModeController import PlayFileModeController


class PlayFileModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        run_file_mode: Event,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
    ):
        super().__init__(daemon=True, name="PlayFileModeThread")
        self.run_file_mode = run_file_mode
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.play_file_mode_controller = PlayFileModeController(
            self.lcd, self.midi_note_on_handler
        )

    def __show_init_message(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(0, 1)
        self.lcd.printout("Prehravani MIDI")

    def __run_file_mode(self):
        self.__show_init_message()
        self.play_file_mode_controller.run(self.run_file_mode)

    def run(self):
        while True:
            sleep(1)
            if self.run_file_mode.is_set():
                print("wanna play file...")
                acquired = PlayFileModeThread.internal_lock.acquire(blocking=False)
                if acquired:
                    try:
                        print(
                            "PlayFileModeThread lock acquired! Starting 'play file mode'..."
                        )
                        t = Thread(target=self.__run_file_mode, name="FileModeRunner")
                        t.start()
                        t.join()
                        print("...ending 'play file mode'.")
                    finally:
                        print("Releasing PlayFileModeThread lock.")
                        PlayFileModeThread.internal_lock.release()
                else:
                    print("but is already playing file :/")
