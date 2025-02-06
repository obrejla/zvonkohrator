from MidiCommandHandler import NOTE_ON_BYTE, MidiCommandHandler


class KeyboardRecordNoteOnHandler(MidiCommandHandler):
    def __init__(self):
        super().__init__()
        self.delays_and_notes = []

    def handles(self, cmd: str):
        return cmd[2:3] == NOTE_ON_BYTE

    def handle(self, msg, dt):
        note = msg[1]
        # velocity = msg[2]
        self.delays_and_notes.append((note, dt))

    def write_to_file(self, team_record_file_path):
        with open(team_record_file_path, "w") as f:
            for delay_and_note in self.delays_and_notes:
                f.write(f"{delay_and_note[0]}:{delay_and_note[1]}\n")
