from mido import MidiFile
from MidiNoteOnHandler import MidiNoteOnHandler
import time

def extract_note_on_messages_in_absolute_time(midi_file: MidiFile):
    note_on_messages_in_absolute_time = {}
    current_time = 0
    prev_note_on_time = 0
    for msg in midi_file:
        if not msg.is_meta:
            current_time += msg.time
            if msg.type == "note_on":
                msg.time = current_time - prev_note_on_time
                if current_time in note_on_messages_in_absolute_time:
                    note_on_messages_in_absolute_time[current_time].append(msg)
                else:
                    note_on_messages_in_absolute_time[current_time] = [msg]
                prev_note_on_time = current_time
    return note_on_messages_in_absolute_time

def play_from_time_position(midi_file: MidiFile, midi_note_on_handler: MidiNoteOnHandler, start_time_position: int = 0):
    extracted_messages = extract_note_on_messages_in_absolute_time(midi_file)
    absolute_times = list(extracted_messages.keys())
    num_of_absolute_times = len(absolute_times)
    if start_time_position < 0 or start_time_position > num_of_absolute_times - 1:
        raise ValueError(f"Position {start_time_position} is out of bounds! [0, {num_of_absolute_times - 1}]")
    for current_time_position in range(start_time_position, num_of_absolute_times):
        current_time = absolute_times[current_time_position]
        for msg in extracted_messages[current_time]:
            time.sleep(msg.time)
            print(msg)
            midi_note_on_handler.handle(msg.note, msg.velocity)

if __name__ == "__main__":
    midi_file = MidiFile("./zvonkohrator-pi-5/midi-files/skakal-pes.mid")
    # midi_file = MidiFile("./zvonkohrator-pi-5/midi-files/kdyz-se-ten-talinskej-rybnik.mid")

    class MidiNoteOnPrintHandler(MidiNoteOnHandler):
        def handle_note_on(self, note, velocity):
            print(f"{note} - {velocity}")

        def handle(self, msg, dt: int):
            pass

        def handles(self, cmd):
            return True

    play_from_time_position(midi_file, MidiNoteOnPrintHandler(), 6)
