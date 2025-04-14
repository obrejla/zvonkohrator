from threading import Event
from unittest.mock import MagicMock, patch

import pytest
from mido import Message, MetaMessage

from zvonkohrator_pi_5.midiutils import (
    Msg,
    convert_recorded_messages_to_absolute_time,
    extract_file_name,
    extract_note_on_messages_in_absolute_time,
    play_from_time_position,
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


def test_msg_parsing():
    msg = Msg("12.5:64:100")
    assert msg.time == 12.5
    assert msg.note == 64
    assert msg.velocity == 100


def test_convert_recorded_messages_to_absolute_time_single_line(tmp_path):
    file_content = "10:64:100\n"
    file_path = tmp_path / "recording.txt"
    file_path.write_text(file_content)

    result = convert_recorded_messages_to_absolute_time(str(file_path))

    assert list(result.keys()) == [10.0]
    msg = result[10.0][0]
    assert msg.time == 10.0
    assert msg.note == 64
    assert msg.velocity == 100


def test_convert_recorded_messages_to_absolute_time_multiple_lines(tmp_path):
    file_content = "10:60:100\n5:62:110\n3:64:120\n"
    file_path = tmp_path / "recording.txt"
    file_path.write_text(file_content)

    result = convert_recorded_messages_to_absolute_time(str(file_path))

    expected_times = [10.0, 15.0, 18.0]
    assert list(result.keys()) == expected_times

    # Check msg.time values (relative to previous note)
    assert result[10.0][0].time == 10.0
    assert result[15.0][0].time == 5.0
    assert result[18.0][0].time == 3.0

    assert result[10.0][0].note == 60
    assert result[15.0][0].note == 62
    assert result[18.0][0].note == 64


def test_convert_recorded_messages_to_absolute_time_duplicate_timestamps(tmp_path):
    file_content = "5:60:100\n5:61:100\n"
    file_path = tmp_path / "recording.txt"
    file_path.write_text(file_content)

    result = convert_recorded_messages_to_absolute_time(str(file_path))

    # First message at time 5.0
    # Second message at time 10.0 (5 + 5)
    assert 5.0 in result
    assert 10.0 in result

    assert result[5.0][0].note == 60
    assert result[10.0][0].note == 61


@pytest.fixture
def extracted_messages():
    return {
        0.0: [Msg("0:60:100")],
        1.0: [Msg("1:61:100")],
        3.0: [Msg("2:62:100")],
    }


def test_play_from_time_position_plays_correctly(extracted_messages):
    note_on_handler = MagicMock()
    interrupt_event = Event()
    start_position = 0

    with patch("time.sleep") as mock_sleep:
        play_from_time_position(
            extracted_messages, note_on_handler, start_position, interrupt_event
        )

    assert note_on_handler.handle_note_on.call_count == 3
    note_on_handler.handle_note_on.assert_any_call(60, 100)
    note_on_handler.handle_note_on.assert_any_call(61, 100)
    note_on_handler.handle_note_on.assert_any_call(62, 100)

    # Ensure time.sleep was called with correct, relative, values
    mock_sleep.assert_any_call(0.0)
    mock_sleep.assert_any_call(1.0)
    mock_sleep.assert_any_call(2.0)


def test_play_from_time_position_stops_on_interrupt_before_first_note_handling(
    extracted_messages,
):
    note_on_handler = MagicMock()
    interrupt_event = Event()
    start_position = 0
    interrupt_event.set()  # Simulates interruption

    with patch("time.sleep"):
        position = play_from_time_position(
            extracted_messages, note_on_handler, start_position, interrupt_event
        )

    # No messages should be handled
    note_on_handler.handle_note_on.assert_not_called()
    assert position == 0  # stopped at the first index


def test_play_from_time_position_partial_play_then_interrupt(extracted_messages):
    note_on_handler = MagicMock()
    interrupt_event = Event()
    start_position = 0
    calls = {"count": 0}

    def interrupt_after_second_call(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 2:
            interrupt_event.set()

    with patch("time.sleep", side_effect=interrupt_after_second_call):
        position = play_from_time_position(
            extracted_messages, note_on_handler, start_position, interrupt_event
        )

    # First break after second sleep, before second note_on_handler call
    assert note_on_handler.handle_note_on.call_count == 1
    assert position == 1  # interrupted during processing second message


def test_play_from_time_position_with_nonzero_start_position(extracted_messages):
    note_on_handler = MagicMock()
    interrupt_event = Event()
    start_position = 1

    with patch("time.sleep"):
        play_from_time_position(
            extracted_messages, note_on_handler, start_position, interrupt_event
        )

    assert note_on_handler.handle_note_on.call_count == 2
    note_on_handler.handle_note_on.assert_any_call(61, 100)
    note_on_handler.handle_note_on.assert_any_call(62, 100)


@pytest.mark.parametrize("start_position", [-1, 3, 100])
def test_play_from_time_position_invalid_position(extracted_messages, start_position):
    note_on_handler = MagicMock()
    interrupt_event = Event()

    with pytest.raises(ValueError) as exc:
        play_from_time_position(
            extracted_messages, note_on_handler, start_position, interrupt_event
        )

    assert "out of bounds" in str(exc.value)
