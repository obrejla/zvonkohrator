from threading import Event, Lock, Thread
from time import sleep

from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler


class PlayCassetteModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        run_cassette_mode: Event,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
    ):
        super().__init__(daemon=True, name="PlayCassetteModeThread")
        self.run_cassette_mode = run_cassette_mode
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler

    def __show_init_message(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(0, 1)
        self.lcd.printout("Prehravani KAZET")

    def __run_cassette_mode(self):
        self.__show_init_message()
        self.play_cassette_mode_controller.run(self.run_cassette_mode)

    def run(self):
        while True:
            sleep(1)
            if self.run_cassette_mode.is_set():
                print("wanna play cassette...")
                acquired = PlayCassetteModeThread.internal_lock.acquire(blocking=False)
                if acquired:
                    try:
                        print(
                            "PlayFileModeThread lock acquired! Starting 'play file mode'..."
                        )
                        t = Thread(
                            target=self.__run_cassette_mode, name="FileModeRunner"
                        )
                        t.start()
                        t.join()
                        print("...ending 'play cassette mode'.")
                    finally:
                        print("Releasing PlayCassetteModeThread lock.")
                        PlayCassetteModeThread.internal_lock.release()
                else:
                    print("but is already playing cassette :/")
