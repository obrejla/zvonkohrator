from LCD1602.LCD1602Mock import LCD1602Mock
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
lcd = LCD1602Mock(16, 2)

midi_command_handler = MidiCommandHandler(midi_player, lcd)
midi_listener = MidiListener(midi_command_handler)
midi_listener.listen()
