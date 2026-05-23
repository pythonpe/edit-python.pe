from unittest.mock import patch

from edit_python_pe.file_io import _write_authors_file


@patch("edit_python_pe.file_io._read_file")
@patch("edit_python_pe.file_io._append_file")
def test_write_authors_file_file_not_found(mock_append_file, mock_read_file):
    mock_read_file.side_effect = FileNotFoundError()

    _write_authors_file("/fake/repo", ["alias1"], "Test Name", "test@email.com")

    mock_append_file.assert_called_once()
    assert "\nTest Name(alias1) <test@email.com>" in mock_append_file.call_args[0][0]
