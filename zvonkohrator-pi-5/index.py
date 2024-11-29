from LCD1602.LCD1602Mock import LCD1602
from MidiListener import MidiListener
from MidiCommandHandler import MidiCommandHandler
from MidiPlayer import MidiPlayer

# USB hub - domaci
# usb_port = "/dev/cu.usbmodem1201"
# USB hub - cestovni
usb_port = "/dev/cu.usbmodem11101"
midi_player = MidiPlayer(usb_port)
lcd = LCD1602(16, 2)

midi_command_handler = MidiCommandHandler(midi_player, lcd)
midi_listener = MidiListener(midi_command_handler)
midi_listener.listen()

# midi_out = rtmidi.MidiOut()
# midi_out.open_port(ports_dict["MIDI In"]);
#
# note_on = [0x92, 48, 100]
# note_off = [0x82, 48, 0]
#
# midi_out.send_message(note_on)
# time.sleep(1)
# midi_out.send_message(note_off)
