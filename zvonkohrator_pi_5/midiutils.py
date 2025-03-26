import time
from threading import Event

from mido import MidiFile

from zvonkohrator_pi_5.MidiNoteOnHandler import MidiNoteOnHandler


def extract_file_name(file_path: str):
    return file_path.split("/")[-1][0:16]


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


class Msg:
    def __init__(self, line: str):
        split_line = line.strip().split(":")
        self.time = float(split_line[0])
        self.note = int(split_line[1])
        self.velocity = int(split_line[2])


def convert_recorded_messages_to_absolute_time(recording_file_path: str):
    note_on_messages_in_absolute_time = {}
    current_time = 0
    prev_note_on_time = 0
    with open(recording_file_path, "r") as f:
        for line in f:
            msg = Msg(line)
            current_time += msg.time
            msg.time = current_time - prev_note_on_time
            if current_time in note_on_messages_in_absolute_time:
                note_on_messages_in_absolute_time[current_time].append(msg)
            else:
                note_on_messages_in_absolute_time[current_time] = [msg]
            prev_note_on_time = current_time
    return note_on_messages_in_absolute_time


def play_from_time_position(
    extracted_messages,
    midi_note_on_handler: MidiNoteOnHandler,
    start_time_position: int,
    should_interrupt_playing: Event,
):
    absolute_times = list(extracted_messages.keys())
    num_of_absolute_times = len(absolute_times)
    if start_time_position < 0 or start_time_position > num_of_absolute_times - 1:
        raise ValueError(
            f"Position {start_time_position} is out of bounds! [0, {num_of_absolute_times - 1}]"
        )
    for current_time_position in range(start_time_position, num_of_absolute_times):
        current_time = absolute_times[current_time_position]
        for msg in extracted_messages[current_time]:
            time.sleep(msg.time)
            if not should_interrupt_playing.is_set():
                midi_note_on_handler.handle_note_on(msg.note, msg.velocity)
            else:
                return current_time_position
