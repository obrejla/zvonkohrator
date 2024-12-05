from gpiozero import Button
from threading import Event, Lock
from time import sleep

def start_play_file_mode(lock: Lock, should_stop_file_mode: Event, should_stop_keyboard_mode: Event):
    should_stop_keyboard_mode.set()
    with lock:
        print("Lock acquired! Starting 'play file mode'...")
        should_stop_keyboard_mode.clear()
        # dummy loop
        while True and not should_stop_file_mode.is_set():
            print("Running in 'play file mode'...")
            sleep(1)
        should_stop_file_mode.clear()
        print("...ending 'play file mode'. Releasing lock.")

def start_play_keyboard_mode(lock: Lock, should_stop_file_mode: Event, should_stop_keyboard_mode: Event):
    should_stop_file_mode.set()
    with lock:
        print("Lock acquired! Starting 'play keyboard mode'...")
        should_stop_file_mode.clear()
        # dummy loop
        while True and not should_stop_keyboard_mode.is_set():
            print("Running in 'play keyboard mode'...")
            sleep(1)
        should_stop_keyboard_mode.clear()
        print("...ending 'play keyboard mode'. Releasing lock.")

def main():
    play_file_mode_button = Button(9)
    play_keyboard_mode_button = Button(10)

    lock = Lock()
    should_stop_file_mode = Event()
    should_stop_keyboard_mode = Event()

    play_file_mode_button.when_pressed = lambda : start_play_file_mode(lock, should_stop_file_mode, should_stop_keyboard_mode)
    play_keyboard_mode_button.when_pressed = lambda : start_play_keyboard_mode(lock, should_stop_file_mode, should_stop_keyboard_mode)

if __name__ == "__main__":
    main()
