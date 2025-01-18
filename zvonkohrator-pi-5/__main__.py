from signal import SIGTERM, pause, signal
from subprocess import check_call
from threading import Event
from time import sleep

from gpiozero import Button, LEDBoard
from LCD import LCD
from MidiNoteOnHandlerImpl import MidiNoteOnHandlerImpl
from MidiPlayer import MidiPlayer
from PlayerButtonsController import PlayerButtonsController
from PlayFileModeThread import PlayFileModeThread
from PlayKeyboardModeThread import PlayKeyboardModeThread
from TeamButtonsController import TeamButtonsController


def show_init_message(lcd: LCD):
    lcd.clear()
    lcd.set_cursor(2, 0)
    lcd.printout("VYBER HERNI")
    lcd.set_cursor(5, 1)
    lcd.printout("MOD...")


def main(lcd: LCD):
    game_mode_leds = LEDBoard(4, 17, 27, 22)
    game_mode_leds.off()
    play_file_mode_button = Button(9)
    play_keyboard_mode_button = Button(11)
    shutdown_button = Button(14, hold_time=3)

    run_file_mode = Event()
    run_keyboard_mode = Event()

    # USB hub - domaci
    # usb_port = "/dev/cu.usbmodem1201"
    # USB hub - cestovni
    # usb_port = "/dev/cu.usbmodem11101"
    # USB - raspberry
    usb_port = "/dev/ttyACM0"
    midi_player = MidiPlayer(usb_port)
    midi_note_on_handler = MidiNoteOnHandlerImpl(midi_player)

    team_buttons_controller = TeamButtonsController()
    player_buttons_controller = PlayerButtonsController()

    PlayFileModeThread(
        run_file_mode, lcd, midi_note_on_handler, player_buttons_controller
    ).start()
    PlayKeyboardModeThread(
        run_keyboard_mode,
        midi_note_on_handler,
        lcd,
    ).start()

    def switch_to_file_mode():
        run_keyboard_mode.clear()
        run_file_mode.set()
        game_mode_leds.value = (0, 0, 0, 1)

    def switch_to_keyboard_mode():
        run_file_mode.clear()
        run_keyboard_mode.set()
        game_mode_leds.value = (1, 0, 0, 0)

    def shutdown():
        lcd.clear()
        lcd.set_cursor(2, 0)
        lcd.printout("Vypinam...")
        sleep(1)
        lcd.clear()
        check_call(["sudo", "poweroff"])

    play_file_mode_button.when_pressed = switch_to_file_mode
    play_keyboard_mode_button.when_pressed = switch_to_keyboard_mode
    shutdown_button.when_held = shutdown

    show_init_message(lcd)

    def on_sigterm():
        team_buttons_controller.clear_leds()
        game_mode_leds.off()
        lcd.clear()

    signal(SIGTERM, on_sigterm)

    pause()


if __name__ == "__main__":
    lcd = LCD()

    try:
        main(lcd)
    except KeyboardInterrupt:
        lcd.clear()
