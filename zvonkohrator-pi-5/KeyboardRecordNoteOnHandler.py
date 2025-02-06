from time import time_ns

from MidiCommandHandler import NOTE_ON_BYTE, MidiCommandHandler


class KeyboardRecordNoteOnHandler(MidiCommandHandler):
    def __init__(self):
        super().__init__()
        self.delays_notes_velocity = []
        self.last_time = 0

    def handles(self, cmd: str):
        cmd_byte = cmd[2:3]
        return cmd_byte == NOTE_ON_BYTE

    def handle(self, msg, dt):
        note = msg[1]
        velocity = msg[2]
        current_time = time_ns()
        time = (current_time - self.last_time) / 1000000000
        self.last_time = current_time
        self.delays_notes_velocity.append(
            [
                time if len(self.delays_notes_velocity) else 0.5,
                note,
                velocity,
            ]
        )

    def write_to_file(self, team_record_file_path):
        with open(team_record_file_path, "w") as f:
            for delay_note_velocity in self.delays_notes_velocity:
                f.write(
                    f"{delay_note_velocity[0]}:{delay_note_velocity[1]}:{delay_note_velocity[2]}\n"
                )
