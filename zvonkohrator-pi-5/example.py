# MIDI - send messages
#
# midi_out = rtmidi.MidiOut()
# midi_out.open_port(ports_dict["MIDI In"]);
#
# note_on = [0x92, 48, 100]
# note_off = [0x82, 48, 0]
#
# midi_out.send_message(note_on)
# time.sleep(1)
# midi_out.send_message(note_off)
