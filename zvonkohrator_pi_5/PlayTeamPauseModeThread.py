from threading import Event, Lock, Thread
from time import sleep

from zvonkohrator_pi_5.EnergyController import Energy, EnergyController
from zvonkohrator_pi_5.FilePlayerController import FilePlayerController
from zvonkohrator_pi_5.LCD import LCD
from zvonkohrator_pi_5.MidiNoteOnHandler import MidiNoteOnHandler
from zvonkohrator_pi_5.PlayerButtonsController import PlayerButtonsController
from zvonkohrator_pi_5.TeamButtonsController import Team, TeamButtonsController


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
        self.run_team_pause_mode = run_team_mode
        self.lcd = lcd
        self.midi_note_on_handler = midi_note_on_handler
        self.team_buttons_controller = team_buttons_controller
        self.player_buttons_controller = player_buttons_controller
        self.file_player_controller = FilePlayerController(
            self.energy_controller,
            self.lcd,
            self.midi_note_on_handler,
            player_buttons_controller,
        )
        self.team_press_lock = Lock()
        self.team_press_list = []

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

        self.player_buttons_controller.add_on_stop_pressed(self.__clear_teams)
        self.player_buttons_controller.add_on_play_pause_pressed(self.__clear_teams)
        self.team_buttons_controller.add_on_pressed(self.__handle_team_pressed)
        self.energy_controller.add_energy_flow_listener(
            self.__handle_energy_flow_change
        )

        self.file_player_controller.run(self.run_team_pause_mode)

        self.team_buttons_controller.remove_on_pressed(self.__handle_team_pressed)
        self.player_buttons_controller.remove_on_stop_pressed(self.__clear_teams)
        self.player_buttons_controller.remove_on_play_pause_pressed(self.__clear_teams)
        self.energy_controller.remove_energy_flow_listener(
            self.__handle_energy_flow_change
        )

        self.__clear_teams()

    def __clear_teams(self):
        self.team_buttons_controller.clear_leds()
        self.team_press_list.clear()

    def __display_teams_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)
        self.lcd.printout(f"PAUSED!     1:{self.team_press_list[0].value}")
        if len(self.team_press_list) > 1:
            self.lcd.set_cursor(0, 1)
            self.lcd.printout(f"2:{self.team_press_list[1].value}".ljust(16))
        if len(self.team_press_list) > 2:
            self.lcd.set_cursor(6, 1)
            self.lcd.printout(f"3:{self.team_press_list[2].value}".ljust(10))
        if len(self.team_press_list) > 3:
            self.lcd.set_cursor(12, 1)
            self.lcd.printout(f"4:{self.team_press_list[3].value}")

    def __display_teams(self):
        self.lcd.bulk_modify(self.__display_teams_bulk)

    def __handle_team_pressed(self, team_id: Team):
        print(f"Wanna handle team button press - team pause ({team_id})...")
        if (
            self.file_player_controller.is_playing.is_set()
            or self.file_player_controller.is_paused.is_set()
        ):
            self.file_player_controller.handle_pause()
            self.team_press_lock.acquire()
            try:
                if (
                    team_id not in self.team_press_list
                    and len(self.team_press_list) < 4
                ):
                    self.team_press_list.append(team_id)
                    self.team_buttons_controller.turn_led_on(team_id)
                    self.__display_teams()
            finally:
                self.team_press_lock.release()
        else:
            print("...but song is neither playing nor paused.")

    def __handle_energy_flow_change(self, new_energy_state: Energy):
        if new_energy_state == Energy.NONE:
            self.__clear_teams()

    def run(self):
        while True:
            if self.run_team_pause_mode.wait():
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
