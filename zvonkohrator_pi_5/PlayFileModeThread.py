from threading import Event, Lock, Thread
from time import sleep

from zvonkohrator_pi_5.EnergyController import EnergyController
from zvonkohrator_pi_5.FilePlayerController import FilePlayerController
from zvonkohrator_pi_5.LCD import LCD
from zvonkohrator_pi_5.MidiNoteOnHandler import MidiNoteOnHandler
from zvonkohrator_pi_5.PlayerButtonsController import PlayerButtonsController
from zvonkohrator_pi_5.TeamButtonsController import Team, TeamButtonsController


class DummyTeamButtonsController(TeamButtonsController):
    def clear_leds(self):
        pass

    def turn_led_on(self, team_id: Team):
        pass

    def add_on_pressed(self, on_pressed_listener):
        pass

    def remove_on_pressed(self, on_pressed_listener):
        pass


class PlayFileModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        energy_controller: EnergyController,
        run_file_mode: Event,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
        player_buttons_controller: PlayerButtonsController,
    ):
        super().__init__(daemon=True, name="PlayFileModeThread")
        self.energy_controller = energy_controller
        self.run_file_mode = run_file_mode
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.file_player_controller = FilePlayerController(
            self.energy_controller,
            self.lcd,
            self.midi_note_on_handler,
            player_buttons_controller,
            DummyTeamButtonsController(),
        )

    def __show_init_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(2, 1)
        self.lcd.printout("File Player")
        sleep(1)

    def __show_init_message(self):
        self.lcd.bulk_modify(self.__show_init_message_bulk)

    def __run_file_mode(self):
        self.__show_init_message()
        self.file_player_controller.run(self.run_file_mode)

    def run(self):
        while True:
            if self.run_file_mode.wait():
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
