import os
import random

from midiutil import MIDIFile


# Function for generation of the random note lengts
def random_note_length():
    lengths = [1, 2]  # eight, quarter note
    return random.choice(lengths)


# Function for generation of the random melody
def generate_melody(num_notes):
    notes = [
        "C2",
        "C#2",
        "D2",
        "D#2",
        "E2",
        "F2",
        "F#2",
        "G2",
        "G#2",
        "A2",
        "B2",
        "H2",
        "C3",
        "C#3",
        "D3",
        "D#3",
        "E3",
        "F3",
        "F#3",
        "G3",
        "G#3",
        "A3",
        "B3",
        "H3",
        "C4",
    ]
    melody = []
    lengths = []

    for _ in range(num_notes):
        while True:
            note = random.choice(notes)
            if len(melody) == 0 or note != melody[-1]:
                melody.append(note)
                lengths.append(random_note_length())
                break

    return melody, lengths


# Function for transfer of the note name to MIDI note value
def note_to_int(note):
    note_map = {
        "C2": 48,
        "C#2": 49,
        "D2": 50,
        "D#2": 51,
        "E2": 52,
        "F2": 53,
        "F#2": 54,
        "G2": 55,
        "G#2": 56,
        "A2": 57,
        "B2": 58,
        "H2": 59,
        "C3": 60,
        "C#3": 61,
        "D3": 62,
        "D#3": 63,
        "E3": 64,
        "F3": 65,
        "F#3": 66,
        "G3": 67,
        "G#3": 68,
        "A3": 69,
        "B3": 70,
        "H3": 71,
        "C4": 72,
    }
    return note_map[note]


# Function to change one tone in the melody
def modify_melody(melody):
    notes = [
        "C2",
        "C#2",
        "D2",
        "D#2",
        "E2",
        "F2",
        "F#2",
        "G2",
        "G#2",
        "A2",
        "B2",
        "H2",
        "C3",
        "C#3",
        "D3",
        "D#3",
        "E3",
        "F3",
        "F#3",
        "G3",
        "G#3",
        "A3",
        "B3",
        "H3",
        "C4",
    ]
    index = random.randint(0, len(melody) - 1)
    original_note = melody[index]
    while True:
        new_note = random.choice(notes)
        if new_note != original_note:
            melody[index] = new_note
            break
    return melody


# Function for gathering version number
def get_version_number():
    files = [f for f in os.listdir() if f.startswith("Melodie v-")]
    if not files:
        return 1
    else:
        versions = [int(f.split("-")[1].split(",")[0]) for f in files]
        return max(versions) + 1


# Ask user for the number of tones
num_notes = int(input("Zadejte celkovy pocet tonu: "))

# Cration of the new MIDI file with the one track
midi = MIDIFile(1)

# Setting tempo (200 BPM)
tempo = 200
midi.addTempo(0, 0, tempo)

# Generation of the melody
melody, lengths = generate_melody(num_notes)

# Selection of the random repetition for the change
modified_index = random.randint(0, 3)

# Addition of a melody repetition to the track
time = 0
for i in range(4):
    if i == modified_index:
        modified_melody = modify_melody(melody.copy())
        for note, length in zip(modified_melody, lengths):
            midi.addNote(0, 0, note_to_int(note), time, length, 100)
            time += length
    else:
        for note, length in zip(melody, lengths):
            midi.addNote(0, 0, note_to_int(note), time, length, 100)
            time += length
    # Pause for two tacts between repetitions
    time += 8

# Getting version number
version_number = get_version_number()

# Filename creation
file_name = (
    f"Melodie v-{version_number}, tonu-{num_notes}, zmena-{modified_index + 1}.mid"
)

# Saving MIDI file
with open(file_name, "wb") as f:
    midi.writeFile(f)

print(f"Zmena v opakovani c.: {modified_index + 1}")
print(f"MIDI soubor '{file_name}' byl vytvoren.")
