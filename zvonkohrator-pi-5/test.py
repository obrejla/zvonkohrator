from gpiozero import Button
from signal import pause
from mido import MidiFile
from MidiCommandHandler import MidiCommandHandler
from MidiPlayer import MidiPlayer
from LCD import LCD
import time

usb_port = "/dev/ttyACM0"
midi_player = MidiPlayer(usb_port)
lcd = LCD()

midi_command_handler = MidiCommandHandler(midi_player, lcd)

prev_button = Button(26)
stop_button = Button(19)
play_pause_button = Button(13)
next_button = Button(6)

midi_file = MidiFile("/home/david/Projects/zvonkohrator/zvonkohrator-pi-5/midi-files/kdyz-se-ten-talinskej-rybnik.mid")
is_playing = False

def play_midi_file():
    global is_playing
    if is_playing:
        print("...pausing file {midi_file.filename}")
        is_playing = False
    else:
        print(f"Playing midi file {midi_file.filename}...")
        is_playing = True
        for msg in midi_file:
            if not msg.is_meta:
                time.sleep(msg.time)
                if msg.type == "note_on" and msg.channel == 1:
                    print(msg)
                    midi_command_handler.note_on(msg.note, msg.velocity)
        print(f"END OF CHANNEL!!! file length={midi_file.length}")

prev_button.when_pressed = lambda : print("PREV button pressed")
stop_button.when_pressed = lambda : print("STOP button pressed")
play_pause_button.when_pressed = play_midi_file
next_button.when_pressed = lambda : print("NEXT button pressed")

pause()


# Exception in thread Thread-1:
# Traceback (most recent call last):
#   File "/usr/lib/python3.11/threading.py", line 1038, in _bootstrap_inner
#     self.run()
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/lgpio.py", line 554, in run
#     cb.func(chip, gpio, level, tick)
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/gpiozero/pins/lgpio.py", line 248, in _call_when_changed
#     super()._call_when_changed(ticks / 1000000000, level)
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/gpiozero/pins/local.py", line 111, in _call_when_changed
#     super()._call_when_changed(
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/gpiozero/pins/pi.py", line 618, in _call_when_changed
#     method(ticks, state)
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/gpiozero/input_devices.py", line 179, in _pin_changed
#     self._fire_events(ticks, bool(self._state_to_value(state)))
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/gpiozero/mixins.py", line 385, in _fire_events
#     self._fire_activated()
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/gpiozero/mixins.py", line 431, in _fire_activated
#     super()._fire_activated()
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/gpiozero/mixins.py", line 348, in _fire_activated
#     self.when_activated()
#   File "/home/david/Projects/zvonkohrator/zvonkohrator-pi-5/test.py", line 36, in play_midi_file
#     midi_command_handler.note_on(msg.note, msg.velocity)
#   File "/home/david/Projects/zvonkohrator/zvonkohrator-pi-5/MidiCommandHandler.py", line 117, in note_on
#     self.midi_player.on_note_on(playable_tone)
#   File "/home/david/Projects/zvonkohrator/zvonkohrator-pi-5/MidiPlayer.py", line 10, in on_note_on
#     response = self.serial.readline().strip()
#                ^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/david/Projects/zvonkohrator/venv/lib/python3.11/site-packages/serial/serialposix.py", line 595, in read
#     raise SerialException(
# serial.serialutil.SerialException: device reports readiness to read but returned no data (device disconnected or multiple access on port?)
