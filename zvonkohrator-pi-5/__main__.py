from gpiozero import Button
from threading import Event, Lock, Thread
from time import sleep
from signal import pause
from MidiListener import MidiListener
from MidiCommandHandlers import MidiCommandHandlers
from MidiNoteOnHandlerImpl import MidiNoteOnHandlerImpl
from MidiPlayer import MidiPlayer

class PlayFileModeThread(Thread):

    internal_lock = Lock()

    def __init__(self, lock: Lock, should_stop_file_mode: Event, should_stop_keyboard_mode: Event):
        super().__init__(daemon=True)
        self.lock = lock
        self.should_stop_file_mode = should_stop_file_mode
        self.should_stop_keyboard_mode = should_stop_keyboard_mode

    def run(self):
        print("wanna play file...")
        if not PlayFileModeThread.internal_lock.locked():
            PlayFileModeThread.internal_lock.acquire()
            self.should_stop_keyboard_mode.set()
            with self.lock:
                print("Lock acquired! Starting 'play file mode'...")
                self.should_stop_keyboard_mode.clear()
                # dummy loop
                while True and not self.should_stop_file_mode.is_set():
                    print("Running in 'play file mode'...")
                    sleep(1)
                self.should_stop_file_mode.clear()
                print("...ending 'play file mode'. Releasing lock.")
            PlayFileModeThread.internal_lock.release()
        else:
            print("but is already playing file :/")


class PlayKeyboardModeThread(Thread):

    internal_lock = Lock()

    def __init__(self, lock: Lock, should_stop_file_mode: Event, should_stop_keyboard_mode: Event, midi_player: MidiPlayer):
        super().__init__(daemon=True)
        self.lock = lock
        self.should_stop_file_mode = should_stop_file_mode
        self.should_stop_keyboard_mode = should_stop_keyboard_mode
        self.midi_player = midi_player

    def __run_keyboard_mode(self):
        midi_note_on_handler = MidiNoteOnHandlerImpl(self.midi_player)
        midi_command_handlers = MidiCommandHandlers()
        midi_command_handlers.register(midi_note_on_handler)
        midi_listener = MidiListener(midi_command_handlers)
        midi_listener.listen(self.should_stop_keyboard_mode)

    def run(self):
        print("wanna play keyboard...")
        if not PlayKeyboardModeThread.internal_lock.locked():
            PlayKeyboardModeThread.internal_lock.acquire()
            self.should_stop_file_mode.set()
            with self.lock:
                print("Lock acquired! Starting 'play keyboard mode'...")
                self.should_stop_file_mode.clear()
                self.__run_keyboard_mode()
                self.should_stop_keyboard_mode.clear()
                print("...ending 'play keyboard mode'. Releasing lock.")
            PlayKeyboardModeThread.internal_lock.release()
        else:
            print("...but it is already playing keyboard :/")


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
