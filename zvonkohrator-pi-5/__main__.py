from gpiozero import Button
from threading import Event, Lock
from signal import pause
from MidiPlayer import MidiPlayer
from PlayFileModeThread import PlayFileModeThread
from PlayKeyboardModeThread import PlayKeyboardModeThread

def main():
    play_file_mode_button = Button(9)
    play_keyboard_mode_button = Button(11)

    lock = Lock()
    should_stop_file_mode = Event()
    should_stop_keyboard_mode = Event()

    # USB hub - domaci
    # usb_port = "/dev/cu.usbmodem1201"
    # USB hub - cestovni
    # usb_port = "/dev/cu.usbmodem11101"
    # USB - raspberry
    usb_port = "/dev/ttyACM0"
    midi_player = MidiPlayer(usb_port)

    play_file_mode_button.when_pressed = lambda : PlayFileModeThread(lock, should_stop_file_mode, should_stop_keyboard_mode).start()
    play_keyboard_mode_button.when_pressed = lambda : PlayKeyboardModeThread(lock, should_stop_file_mode, should_stop_keyboard_mode, midi_player).start()

    pause()

if __name__ == "__main__":
    main()
