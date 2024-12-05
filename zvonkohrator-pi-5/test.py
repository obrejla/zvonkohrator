from gpiozero import Button
from signal import pause
from mido import MidiFile
from MidiCommandHandler import MidiCommandHandler
from MidiPlayer import MidiPlayer
from LCD import LCD
import time
import os

usb_port = "/dev/ttyACM0"
midi_player = MidiPlayer(usb_port)
lcd = LCD()

midi_command_handler = MidiCommandHandler(midi_player, lcd)

prev_button = Button(26)
stop_button = Button(19)
play_pause_button = Button(13)
next_button = Button(6)

midi_file = MidiFile("./zvonkohrator-pi-5/midi-files/skakal-pes.mid")
is_playing = False
is_paused = False

def extract_file_name(file_path: str):
    return file_path.split("/")[-1][0:16]

def play_midi_file():
    global is_playing
    if is_playing:
        print("...pausing file {midi_file.filename}")
        is_playing = False
    else:
        print(f"Playing midi file {midi_file.filename}...")
        lcd.clear()
        lcd.set_cursor(2, 0)
        lcd.printout("Prehravam...")
        lcd.set_cursor(0, 1)
        lcd.printout(extract_file_name(midi_file.filename))
        is_playing = True
        for msg in midi_file:
            if not msg.is_meta:
                time.sleep(msg.time)
                if msg.type == "note_on":
                    print(msg)
                    midi_command_handler.note_on(msg.note, msg.velocity)
        print(f"END OF CHANNEL!!! file length={midi_file.length}")
        lcd.clear()
        lcd.set_cursor(5, 0)
        lcd.printout("Konec.")
        lcd.set_cursor(0, 1)
        lcd.printout(extract_file_name(midi_file.filename))

def prev_pressed():
    print("PREV button pressed")
    if is_playing or is_paused:
        # notify playing thread to stop
        # reset current playing position to start
        # start playing of the current song
        pass
    else:
        # select prev song from the list
        pass

def play_pause_pressed():
    print("PLAY/PAUSE button pressed")
    play_midi_file()
    if is_playing:
        # notify playing thread to pause - remember current position
        # is_playing = False
        # is_paused = True
        pass
    elif is_paused:
        # notify playing thread to play from remembered position
        # is_playing = True
        # is_paused = False
        pass
    else:
        # start playing current song
        pass

def stop_pressed():
    print("STOP button pressed")
    if is_playing or is_paused:
        # notify playing thread to stop
        # reset current playing position to start
        # is_playing = False
        # is_paused = False
        pass

def next_pressed():
    print("NEXT button pressed")
    if is_playing or is_paused:
        # notify playing thread to stop
        # reset current playing position to start
        pass
    # select next song from list
    # IF IT WAS NOT PAUSED - trigger Play for the song

lcd.clear()
prev_button.when_pressed = prev_pressed
stop_button.when_pressed = stop_pressed
play_pause_button.when_pressed = play_pause_pressed
next_button.when_pressed = next_pressed

try:
    pause()
except KeyboardInterrupt:
    lcd.clear()
