import pytest
from mido import Message, MetaMessage

from zvonkohrator_pi_5.midiutils import (
    extract_file_name,
    extract_note_on_messages_in_absolute_time,
)


class FakeMidiFile:
    def __init__(self, messages):
        self.messages = messages

    def __iter__(self):
        return iter(self.messages)


def test_extract_only_note_on_messages_and_absolute_timing():
    messages = [
        Message("note_on", note=60, velocity=64, time=0),
        Message("note_off", note=60, velocity=64, time=1),
        Message("note_on", note=62, velocity=64, time=2),
        Message("note_on", note=64, velocity=64, time=3),
        MetaMessage("track_name", name="Test", time=1),  # should be ignored
    ]
    midi = FakeMidiFile(messages)

    result = extract_note_on_messages_in_absolute_time(midi)

    # we only have 3 "note_on" messages
    assert len(result) == 3
    keys = sorted(result.keys())
    assert keys == [0, 3, 6]  # absolute time: 0, 0+1+2, 3 more

    # check correct notes in particular times
    assert result[0][0].note == 60
    assert result[3][0].note == 62
    assert result[6][0].note == 64

    # check that msg.time is adjusted relatively to previous note_on
    assert result[0][0].time == 0  # first note_on
    assert result[3][0].time == 3  # difference between 0 and 3
    assert result[6][0].time == 3  # difference 3 and 6


def test_multiple_note_on_at_same_time():
    messages = [
        Message("note_on", note=60, velocity=64, time=0),
        Message("note_on", note=61, velocity=64, time=0),  # same time
        Message("note_on", note=62, velocity=64, time=1),
    ]
    midi = FakeMidiFile(messages)
    result = extract_note_on_messages_in_absolute_time(midi)

    assert 0 in result
    assert 1 in result

    assert len(result[0]) == 2
    assert result[0][0].note == 60
    assert result[0][1].note == 61  # another note but at the same time
    assert result[1][0].note == 62


def test_ignores_meta_messages():
    messages = [
        MetaMessage("track_name", name="SomeName", time=0),
        Message("note_on", note=60, velocity=100, time=1),
        MetaMessage("end_of_track", time=2),
    ]
    midi = FakeMidiFile(messages)
    result = extract_note_on_messages_in_absolute_time(midi)

    assert len(result) == 1  # only one note_on message
    assert 1 in result
    assert result[1][0].note == 60


@pytest.mark.parametrize(
    "file_path, expected",
    [
        ("/home/user/song.mid", "song.mid"),
        ("/some/deep/path/to/music_file_name.mid", "music_file_name."),
        ("justafile.mid", "justafile.mid"),
        ("folder/subfolder/12345678901234567890.mid", "1234567890123456"),
        ("", ""),
        ("/", ""),
        ("/file_with_no_ext", "file_with_no_ext"),
    ],
)
def test_extract_file_name(file_path, expected):
    assert extract_file_name(file_path) == expected
