from threading import Event, Lock, Thread
from time import sleep

from FilePlayerController import FilePlayerController
from LCD import LCD
from MidiNoteOnHandler import MidiNoteOnHandler
from PlayerButtonsController import PlayerButtonsController
from TeamButtonsController import TeamButtonsController


class PlayTeamModeThread(Thread):
    internal_lock = Lock()

    def __init__(
        self,
        energy_flows: Event,
        run_team_mode: Event,
        lcd: LCD,
        midi_note_on_handler: MidiNoteOnHandler,
        player_buttons_controller: PlayerButtonsController,
        team_buttons_controller: TeamButtonsController,
    ):
        super().__init__(daemon=True, name="PlayTeamModeThread")
        self.energy_flows = energy_flows
        self.run_team_mode = run_team_mode
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.file_player_controller = FilePlayerController(
            self.energy_flows,
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
            sleep(1)
            if self.run_team_mode.is_set():
                print("wanna play team...")
                acquired = PlayTeamModeThread.internal_lock.acquire(blocking=False)
                if acquired:
                    try:
                        print(
                            "PlayTeamModeThread lock acquired! Starting 'play team mode'..."
                        )
                        t = Thread(target=self.__run_team_mode, name="TeamModeRunner")
                        t.start()
                        t.join()
                        print("...ending 'play team mode'.")
                    finally:
                        print("Releasing PlayTeamModeThread lock.")
                        PlayTeamModeThread.internal_lock.release()
                else:
                    print("but is already playing team :/")
