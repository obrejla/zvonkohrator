import random

from midiutil import MIDIFile


def calculate_probabilities():
    tones = [
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
    probabilities = [4 / (i + 1) for i in range(len(tones))]
    total = sum(probabilities)
    probabilities = [p / total for p in probabilities]
    return tones, probabilities


# function for MIDI file creation
def create_midi(total_notes, file_name):
    tones, probabilities = calculate_probabilities()
    midi = MIDIFile(1)
    midi.addTempo(0, 0, 220)

    note_length = 0.5  # eight note
    notes_played = 0
    played_tones = []

    while notes_played < total_notes:
        current_note = 48  # C2
        highest_tone = random.choices(tones, probabilities)[0]
        highest_tone_number = (
            tones.index(highest_tone) + 49
        )  # transfer to MIDI note number

        # increment of the scale
        while current_note <= highest_tone_number and notes_played < total_notes:
            midi.addNote(
                0, 0, current_note, notes_played * note_length, note_length, 100
            )
            played_tones.append(current_note)
            current_note += 1
            notes_played += 1

        # decrement of the scale
        if current_note > 49 and notes_played < total_notes:  # C#2 is 49
            current_note = highest_tone_number - 1
            while current_note >= 49 and notes_played < total_notes:
                midi.addNote(
                    0, 0, current_note, notes_played * note_length, note_length, 100
                )
                played_tones.append(current_note)
                current_note -= 1
                notes_played += 1

    # save MIDI file
    with open(f"{file_name}.mid", "wb") as output_file:
        midi.writeFile(output_file)


# main script part
if __name__ == "__main__":
    total_notes = int(input("Zadejte celkovy pocet tonu: "))
    file_name = input("Zadejte nazev souboru: ")
    create_midi(total_notes, file_name)
