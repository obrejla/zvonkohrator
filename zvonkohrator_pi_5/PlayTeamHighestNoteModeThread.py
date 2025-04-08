from threading import Event, Lock, Thread
from time import sleep

from zvonkohrator_pi_5.EnergyController import Energy, EnergyController
from zvonkohrator_pi_5.FilePlayerController import FilePlayerController
from zvonkohrator_pi_5.LCD import LCD
from zvonkohrator_pi_5.MidiNoteOnHandler import MidiNoteOnHandler
from zvonkohrator_pi_5.PlayerButtonsController import PlayerButtonsController
from zvonkohrator_pi_5.TeamButtonsController import Team, TeamButtonsController


class PlayTeamHighestNoteModeThread(Thread):
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
        super().__init__(daemon=True, name="PlayTeamHighestNoteModeThread")
        self.energy_controller = energy_controller
        self.run_team_mode = run_team_mode
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
        self.team_press_list = {
            Team.RED: 0,
            Team.GREEN: 0,
            Team.BLUE: 0,
            Team.YELLOW: 0,
        }

    def __show_init_message_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(2, 0)
        self.lcd.printout("* HERNI MOD *")
        self.lcd.set_cursor(1, 1)
        self.lcd.printout("Team High Note")
        sleep(1)

    def __show_init_message(self):
        self.lcd.bulk_modify(self.__show_init_message_bulk)

    def __run_team_mode(self):
        self.__show_init_message()

        self.file_player_controller.add_on_finish_listener(self.__display_teams)
        self.team_buttons_controller.add_on_pressed(self.__handle_team_pressed)
        self.player_buttons_controller.add_on_prev_pressed(self.__clear_teams)
        self.player_buttons_controller.add_on_stop_pressed(self.__clear_teams)
        self.player_buttons_controller.add_on_next_pressed(self.__clear_teams)
        self.energy_controller.add_energy_flow_listener(
            self.__handle_energy_flow_change
        )

        self.file_player_controller.run(self.run_team_mode)

        self.file_player_controller.remove_on_finish_listener(self.__display_teams)
        self.team_buttons_controller.remove_on_pressed(self.__handle_team_pressed)
        self.player_buttons_controller.remove_on_prev_pressed(self.__clear_teams)
        self.player_buttons_controller.remove_on_stop_pressed(self.__clear_teams)
        self.player_buttons_controller.remove_on_next_pressed(self.__clear_teams)
        self.energy_controller.remove_energy_flow_listener(
            self.__handle_energy_flow_change
        )

        self.__clear_teams()

    def __clear_teams(self):
        self.team_buttons_controller.clear_leds()
        self.team_press_list = {
            Team.RED: 0,
            Team.GREEN: 0,
            Team.BLUE: 0,
            Team.YELLOW: 0,
        }

    def __display_teams_bulk(self):
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)
        self.lcd.printout(
            f"END! {Team.RED.value}:{self.team_press_list[Team.RED]}".ljust(16)
        )
        self.lcd.set_cursor(11, 0)
        self.lcd.printout(
            f"{Team.GREEN.value}:{self.team_press_list[Team.GREEN]}".ljust(5)
        )
        self.lcd.set_cursor(5, 1)
        self.lcd.printout(
            f"     {Team.BLUE.value}:{self.team_press_list[Team.BLUE]}".ljust(16)
        )
        self.lcd.set_cursor(11, 1)
        self.lcd.printout(
            f"{Team.YELLOW.value}:{self.team_press_list[Team.YELLOW]}".ljust(5)
        )

    def __display_teams(self):
        self.lcd.bulk_modify(self.__display_teams_bulk)

    def __handle_team_pressed(self, team_id: Team):
        print(f"Wanna handle team button press ({team_id})...")
        if (
            self.file_player_controller.is_playing.is_set()
            and self.team_press_list[team_id] == 0
        ):
            self.team_press_list[team_id] = self.midi_note_on_handler.get_last_note()
            self.team_buttons_controller.turn_led_on(team_id)
        else:
            print(
                "...but song is neither playing nor paused or team has already voted."
            )

    def __handle_energy_flow_change(self, new_energy_state: Energy):
        if new_energy_state == Energy.NONE:
            self.__clear_teams()

    def run(self):
        while True:
            if self.run_team_mode.wait():
                print("wanna play team highest note...")
                acquired = PlayTeamHighestNoteModeThread.internal_lock.acquire(
                    blocking=False
                )
                if acquired:
                    try:
                        print(
                            "PlayTeamHighestNoteModeThread lock acquired! Starting 'play team hignest note mode'..."
                        )
                        t = Thread(
                            target=self.__run_team_mode,
                            name="TeamHighestNoteModeRunner",
                        )
                        t.start()
                        t.join()
                        print("...ending 'play team highest note mode'.")
                    finally:
                        print("Releasing PlayTeamHighestNoteModeThread lock.")
                        PlayTeamHighestNoteModeThread.internal_lock.release()
                else:
                    print("but is already playing team highest note :/")
