from midiutil import MIDIFile

# Morse code dictionary
morse_code_dict = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
}


# Function to convert text to morse code
def text_to_morse(text):
    morse_code = ""
    for char in text.upper():
        if char in morse_code_dict:
            morse_code += morse_code_dict[char] + "/"
        elif char == " ":
            morse_code += "/"
    return morse_code


# Function to convert morse code to MIDI notes
def morse_to_midi(morse_code):
    midi_notes = []
    for char in morse_code:
        if char == ".":
            midi_notes.append((60, 1))  # C3, quarter note
        elif char == "-":
            midi_notes.append((71, 1))  # H3, quarter note
        elif char == "/":
            midi_notes.append((48, 2))  # C2, half note
    return midi_notes


# Create MIDI file
def create_midi(midi_notes, file_name):
    track = 0
    channel = 0
    time = 0  # In beats
    tempo = 80  # In BPM
    volume = 100  # 0-127, as per MIDI standard

    midi_file = MIDIFile(1)  # One track
    midi_file.addTempo(track, time, tempo)

    for note, duration in midi_notes:
        midi_file.addNote(track, channel, note, time, duration, volume)
        time += duration

    with open(file_name, "wb") as output_file:
        midi_file.writeFile(output_file)


# Prompt user for input text
input_text = input("Zadejte text pro prevod do Morseovy abecedy: ")

# Convert text to morse code
morse_code = text_to_morse(input_text)

# Add three slashes at the end of the sentence
morse_code += "//"

# Convert morse code to MIDI notes
midi_notes = morse_to_midi(morse_code)

# Prompt user for MIDI file name
file_name = input("Zadejte nazev MIDI souboru: ") + ".mid"

# Create and save MIDI file
create_midi(midi_notes, file_name)

print(f"MIDI soubor byl uspesne vytvoren jako '{file_name}'.")
