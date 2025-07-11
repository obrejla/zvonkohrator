from queue import Empty, Queue
from signal import SIGINT, SIGTERM, signal
from subprocess import check_call
from threading import Event, Thread
from time import sleep, time

from gpiozero import Button, LEDBoard

from zvonkohrator_pi_5.EnergyController import Energy, EnergyController
from zvonkohrator_pi_5.LCDImpl import LCDImpl
from zvonkohrator_pi_5.MidiNoteOnHandlerImpl import MidiNoteOnHandlerImpl
from zvonkohrator_pi_5.MidiPlayer import MidiPlayer
from zvonkohrator_pi_5.PlayCassetteModeThread import PlayCassetteModeThread
from zvonkohrator_pi_5.PlayerButtonsController import PlayerButtonsController
from zvonkohrator_pi_5.PlayFileModeThread import PlayFileModeThread
from zvonkohrator_pi_5.PlayKeyboardModeThread import PlayKeyboardModeThread
from zvonkohrator_pi_5.PlayTeamHighestNoteModeThread import (
    PlayTeamHighestNoteModeThread,
)
from zvonkohrator_pi_5.PlayTeamPauseModeThread import PlayTeamPauseModeThread
from zvonkohrator_pi_5.RemoteController import RemoteController
from zvonkohrator_pi_5.TeamButtonsControllerImpl import TeamButtonsControllerImpl
from zvonkohrator_pi_5.utils import show_loading, throttle


def main():
    kill = Event()
    in_shutdown = Event()
    game_mode_leds = LEDBoard(4, 17, 27, 22, active_high=False)
    game_mode_leds.off()
    last_game_mode_leds_queue = Queue()
    play_file_mode_button = Button(9)
    play_keyboard_mode_button = Button(11)
    play_team_mode_button = Button(0)
    play_cassette_mode_button = Button(10)
    shutdown_button = Button(14)

    run_file_mode = Event()
    run_keyboard_mode = Event()
    run_team_pause_mode = Event()
    run_team_highest_note_mode = Event()
    run_cassette_mode = Event()

    energy_controller = EnergyController()
    remote_controller = RemoteController()

    # USB hub - domaci
    # usb_port = "/dev/cu.usbmodem1201"
    # USB hub - cestovni
    # usb_port = "/dev/cu.usbmodem11101"
    # USB - raspberry
    usb_port = "/dev/ttyACM0"
    midi_player = MidiPlayer(usb_port)
    midi_note_on_handler = MidiNoteOnHandlerImpl(midi_player)

    team_buttons_controller = TeamButtonsControllerImpl(energy_controller)
    player_buttons_controller = PlayerButtonsController(
        energy_controller, remote_controller
    )

    lcd = LCDImpl(energy_controller)
    PlayFileModeThread(
        energy_controller,
        run_file_mode,
        lcd,
        midi_note_on_handler,
        player_buttons_controller,
    ).start()
    PlayKeyboardModeThread(
        energy_controller,
        run_keyboard_mode,
        lcd,
        midi_note_on_handler,
        player_buttons_controller,
    ).start()
    PlayTeamPauseModeThread(
        energy_controller,
        run_team_pause_mode,
        lcd,
        midi_note_on_handler,
        player_buttons_controller,
        team_buttons_controller,
    ).start()
    PlayTeamHighestNoteModeThread(
        energy_controller,
        run_team_highest_note_mode,
        lcd,
        midi_note_on_handler,
        player_buttons_controller,
        team_buttons_controller,
    ).start()
    PlayCassetteModeThread(
        energy_controller,
        run_cassette_mode,
        lcd,
        midi_note_on_handler,
        player_buttons_controller,
    ).start()

    def switch_to_file_mode():
        if energy_controller.is_energy_flowing():
            run_keyboard_mode.clear()
            run_team_pause_mode.clear()
            run_cassette_mode.clear()
            run_team_highest_note_mode.clear()
            run_file_mode.set()
            game_mode_leds.value = (0, 0, 0, 1)

    def switch_to_keyboard_mode():
        if energy_controller.is_energy_flowing():
            run_file_mode.clear()
            run_team_pause_mode.clear()
            run_cassette_mode.clear()
            run_team_highest_note_mode.clear()
            run_keyboard_mode.set()
            game_mode_leds.value = (1, 0, 0, 0)

    def switch_to_team_pause_mode():
        if energy_controller.is_energy_flowing():
            run_file_mode.clear()
            run_keyboard_mode.clear()
            run_cassette_mode.clear()
            run_team_highest_note_mode.clear()
            run_team_pause_mode.set()
            game_mode_leds.value = (0, 0, 1, 0)

    def switch_to_team_highest_note_mode():
        if energy_controller.is_energy_flowing():
            run_file_mode.clear()
            run_keyboard_mode.clear()
            run_cassette_mode.clear()
            run_team_pause_mode.clear()
            run_team_highest_note_mode.set()
            game_mode_leds.value = (0, 0, 1, 0)

    def switch_to_cassette_mode():
        if energy_controller.is_energy_flowing():
            run_file_mode.clear()
            run_keyboard_mode.clear()
            run_team_pause_mode.clear()
            run_team_highest_note_mode.clear()
            run_cassette_mode.set()
            game_mode_leds.value = (0, 1, 0, 0)

    def handle_team_mode():
        if energy_controller.is_energy_flowing():
            if run_team_pause_mode.is_set():
                print("TEAM Highest Note!...")
                switch_to_team_highest_note_mode()
            else:
                print("TEAM Pause")
                switch_to_team_pause_mode()

    def show_init_message_bulk():
        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.printout("  ZVONKOHRATOR  ")
        lcd.set_cursor(0, 1)
        lcd.printout("Vyber herni mod!")

    def show_init_message():
        lcd.bulk_modify(show_init_message_bulk)

    def show_shutdown_message_bulk():
        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.printout("Vypinam! Storno?")
        show_loading(lcd, 3, 1, in_shutdown)
        lcd.clear()

    def show_shutdown_message():
        lcd.bulk_modify(show_shutdown_message_bulk)

    def shutdown():
        in_shutdown.set()
        run_file_mode.clear()
        run_keyboard_mode.clear()
        run_team_pause_mode.clear()
        run_cassette_mode.clear()
        run_team_highest_note_mode.clear()
        game_mode_leds.value = (0, 0, 0, 0)
        energy_controller.start_bypass()
        show_shutdown_message()
        if in_shutdown.is_set():
            check_call(["sudo", "poweroff"])

    def interrupt_shutdown():
        energy_controller.stop_bypass()
        if in_shutdown.is_set():
            in_shutdown.clear()
            show_init_message()

    def handle_energy_flow(energy: Energy):
        if energy == Energy.FLOWS:
            try:
                game_mode_leds.value = last_game_mode_leds_queue.get(block=False)
            except Empty:
                print("Empty game mode leds queue! Probably initial state...")
        else:
            last_game_mode_leds_queue.put(game_mode_leds.value)
            game_mode_leds.off()

    play_file_mode_button.when_pressed = switch_to_file_mode
    play_keyboard_mode_button.when_pressed = switch_to_keyboard_mode
    play_team_mode_button.when_pressed = throttle(lambda: handle_team_mode())
    play_cassette_mode_button.when_pressed = switch_to_cassette_mode

    shutdown_press_time = None

    def handle_shutdown_release():
        nonlocal shutdown_press_time
        duration = time() - shutdown_press_time
        if duration >= 2:
            # long press – shutdown
            Thread(
                target=shutdown,
                daemon=True,
                name="HandleShutdownThread",
            ).start()
        else:
            # short press – interrupt
            Thread(
                target=interrupt_shutdown,
                daemon=True,
                name="HandleInterruptShutdownThread",
            ).start()

    def set_shutdown_press_time():
        nonlocal shutdown_press_time
        shutdown_press_time = time()

    shutdown_button.when_pressed = set_shutdown_press_time
    shutdown_button.when_released = handle_shutdown_release

    energy_controller.init()
    energy_controller.add_energy_flow_listener(handle_energy_flow)
    show_init_message()

    def on_kill(signum, frame):
        kill.set()

    signal(SIGTERM, on_kill)
    signal(SIGINT, on_kill)

    while not kill.is_set():
        sleep(1)

    team_buttons_controller.clear_leds()
    game_mode_leds.off()
    energy_controller.energy_flows.set()  # just a little bit of hack to enable followup LCD.clear() before terminating
    lcd.bulk_modify(lcd.clear)


if __name__ == "__main__":
    main()
