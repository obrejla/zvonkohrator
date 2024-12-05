from MidiListener import MidiListener
from MidiCommandHandlers import MidiCommandHandlers
from MidiNoteOnHandlerImpl import MidiNoteOnHandlerImpl
from MidiPlayer import MidiPlayer

# USB hub - domaci
# usb_port = "/dev/cu.usbmodem1201"
# USB hub - cestovni
# usb_port = "/dev/cu.usbmodem11101"
# USB - raspberry
usb_port = "/dev/ttyACM0"
midi_player = MidiPlayer(usb_port)

midi_note_on_handler = MidiNoteOnHandlerImpl(midi_player)
midi_command_handlers = MidiCommandHandlers()
midi_command_handlers.register(midi_note_on_handler)
midi_listener = MidiListener(midi_command_handlers)
midi_listener.listen()
