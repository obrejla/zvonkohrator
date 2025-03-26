import pytest

from zvonkohrator_pi_5.midiutils import extract_file_name


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
