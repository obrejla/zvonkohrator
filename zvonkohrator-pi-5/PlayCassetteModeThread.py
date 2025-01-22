from threading import Event, Lock, Thread
from time import sleep

from CassetteDetector import CassetteDetector
from CassettePlayerController import CassettePlayerController
from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler
from PlayerButtonsController import PlayerButtonsController


class PlayCassetteModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        energy_flows: Event,
        run_cassette_mode: Event,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
        player_buttons_controller: PlayerButtonsController,
    ):
        super().__init__(daemon=True, name="PlayCassetteModeThread")
        self.energy_flows = energy_flows
        self.run_cassette_mode = run_cassette_mode
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.player_buttons_controller = player_buttons_controller
        self.cassette_player_controller = CassettePlayerController(
            self.energy_flows,
            self.lcd,
            self.midi_note_on_handler,
            self.player_buttons_controller,
            CassetteDetector(self.energy_flows),
        )

    def __show_init_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(0, 1)
        self.lcd.printout("Cassette Player")
        sleep(1)

    def __show_init_message(self):
        self.lcd.bulk_modify(self.__show_init_message_bulk)

    def __run_cassette_mode(self):
        self.__show_init_message()
        self.cassette_player_controller.run(self.run_cassette_mode)

    def run(self):
        while True:
            if self.run_cassette_mode.wait():
                print("wanna play cassette...")
                acquired = PlayCassetteModeThread.internal_lock.acquire(blocking=False)
                if acquired:
                    try:
                        print(
                            "PlayCassetteModeThread lock acquired! Starting 'play cassette mode'..."
                        )
                        t = Thread(
                            target=self.__run_cassette_mode, name="CassetteModeRunner"
                        )
                        t.start()
                        t.join()
                        print("...ending 'play cassette mode'.")
                    finally:
                        print("Releasing PlayCassetteModeThread lock.")
                        PlayCassetteModeThread.internal_lock.release()
                else:
                    print("but is already playing cassette :/")
