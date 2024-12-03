from LCD import LCD
from MidiListener import MidiListener
from MidiCommandHandler import MidiCommandHandler
from MidiPlayer import MidiPlayer

# USB hub - domaci
# usb_port = "/dev/cu.usbmodem1201"
# USB hub - cestovni
# usb_port = "/dev/cu.usbmodem11101"
# USB - raspberry
usb_port = "/dev/ttyACM0"
midi_player = MidiPlayer(usb_port)
lcd = LCD()

midi_command_handler = MidiCommandHandler(midi_player, lcd)
midi_listener = MidiListener(midi_command_handler)
midi_listener.listen()
