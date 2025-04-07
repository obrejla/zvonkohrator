from threading import Event, Lock, Thread
from time import sleep

from zvonkohrator_pi_5.EnergyController import EnergyController
from zvonkohrator_pi_5.FilePlayerController import FilePlayerController
from zvonkohrator_pi_5.LCD import LCD
from zvonkohrator_pi_5.MidiNoteOnHandler import MidiNoteOnHandler
from zvonkohrator_pi_5.PlayerButtonsController import PlayerButtonsController
from zvonkohrator_pi_5.TeamButtonsController import TeamButtonsController


class PlayTeamPauseModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        energy_controller: EnergyController,
        run_team_mode: Event,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
        player_buttons_controller: PlayerButtonsController,
        team_buttons_controller: TeamButtonsController,
    ):
        super().__init__(daemon=True, name="PlayTeamPauseModeThread")
        self.energy_controller = energy_controller
        self.run_team_mode = run_team_mode
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.file_player_controller = FilePlayerController(
            self.energy_controller,
            self.lcd,
            self.midi_note_on_handler,
            player_buttons_controller,
            team_buttons_controller,
        )

    def __show_init_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(3, 1)
        self.lcd.printout("Team Pause")
        sleep(1)

    def __show_init_message(self):
        self.lcd.bulk_modify(self.__show_init_message_bulk)

    def __run_team_mode(self):
        self.__show_init_message()
        self.file_player_controller.run(self.run_team_mode)

    def run(self):
        while True:
            if self.run_team_mode.wait():
                print("wanna play team pause...")
                acquired = PlayTeamPauseModeThread.internal_lock.acquire(blocking=False)
                if acquired:
                    try:
                        print(
                            "PlayTeamPauseModeThread lock acquired! Starting 'play team pause mode'..."
                        )
                        t = Thread(
                            target=self.__run_team_mode, name="TeamPauseModeRunner"
                        )
                        t.start()
                        t.join()
                        print("...ending 'play team pause mode'.")
                    finally:
                        print("Releasing PlayTeamPauseModeThread lock.")
                        PlayTeamPauseModeThread.internal_lock.release()
                else:
                    print("but is already playing team pause :/")
