import os
import time
from queue import Queue
from threading import Thread

from serial import Serial, SerialException


class MidiPlayer:
    def __init__(self, usb_port: str):
        self.serial = None
        self.notes_queue = Queue()
        self._connect_serial(usb_port, 115200, 10)
        self.worker_thread = Thread(
            target=self.__write_worker, daemon=True, name="SerialWriter"
        ).start()

    def _connect_serial(self, usb_port: str, baudrate: int, max_retries: int):
        retries = 0
        while retries < max_retries:
            if not os.path.exists(usb_port):
                print(f"[MidiPlayer] Waiting for USB device {usb_port} to appear...")
                time.sleep(0.5)
                retries += 1
                continue

            try:
                self.serial = Serial(usb_port, baudrate)
                print(f"[MidiPlayer] Serial connection established on {usb_port}")
                return
            except SerialException as e:
                print(f"[MidiPlayer] Serial exception: {e}")
                retries += 1
                time.sleep(1)

        raise RuntimeError(
            f"[MidiPlayer] Failed to initialize Serial on {usb_port} after {max_retries} retries."
        )

    def __write_worker(self):
        while True:
            playable_tone = self.notes_queue.get()
            if playable_tone is None:
                break
            if self.serial:
                try:
                    self.serial.write(f"{playable_tone}\r".encode())
                except SerialException as e:
                    print(f"[MidiPlayer] Write error: {e}")

    def on_note_on(self, playable_tone: int):
        self.notes_queue.put(playable_tone)

    def on_note_off(self, playable_tone: int):
        self.notes_queue.put(playable_tone * -1)
