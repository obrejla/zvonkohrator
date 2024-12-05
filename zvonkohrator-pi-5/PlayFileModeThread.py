from threading import Event, Lock, Thread
from time import sleep

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
