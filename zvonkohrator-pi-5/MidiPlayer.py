from queue import Queue
from threading import Thread

from serial import Serial


class MidiPlayer:
    def __init__(self, usb_port: str):
        self.serial = Serial(usb_port, 115200)
        self.notes_queue = Queue()
        self.worker_thread = Thread(target=self.__write_worker, daemon=True).start()

    def __write_worker(self):
        while True:
            playable_tone = self.notes_queue.get()
            if playable_tone is None:
                break
            self.serial.write(f"{playable_tone}\r".encode())

    def on_note_on(self, playable_tone: int):
        self.notes_queue.put(playable_tone)

    def on_note_off(self, playable_tone: int):
        self.notes_queue.put(playable_tone * -1)
