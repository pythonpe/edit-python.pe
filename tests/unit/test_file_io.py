from unittest.mock import MagicMock, patch

from edit_python_pe.file_io import (
    _append_file,
    _read_file,
    _write_authors_file,
    _write_file,
)


class TestFileIO:
    def test_write_authors_file(self):
        repo_path = "/fake/repo"
        aliases = ["alias1"]
        name = "Test Name"
        email = "test@email.com"
        file_path = f"{repo_path}/AUTHORS"

        # Case: author not present, should append
        with (
            patch(
                "edit_python_pe.file_io._read_file", return_value=""
            ) as mock_read_file,
            patch("edit_python_pe.file_io._append_file") as mock_append_file,
        ):
            _write_authors_file(repo_path, aliases, name, email)
            mock_read_file.assert_called_once_with(file_path)
            mock_append_file.assert_called_once()
            args, _ = mock_append_file.call_args
            assert name in args[0]
            assert email in args[0]

        # Case: author already present, should not append
        existing_line = f"\n{name}(alias1) <{email}>"
        with (
            patch(
                "edit_python_pe.file_io._read_file", return_value=existing_line
            ) as mock_read_file,
            patch("edit_python_pe.file_io._append_file") as mock_append_file,
        ):
            _write_authors_file(repo_path, aliases, name, email)
            mock_read_file.assert_called_once_with(file_path)
            mock_append_file.assert_not_called()

    def test_read_file(self):
        file_path = "/tmp/testfile.txt"
        expected_content = "Hello, world!"
        from unittest.mock import mock_open

        with patch(
            "builtins.open", mock_open(read_data=expected_content)
        ) as mock_open_file:
            result = _read_file(file_path)
            mock_open_file.assert_called_with(file_path, encoding="utf-8")
            assert result == expected_content

    def test_append_file(self):
        file_content = "Append this!"
        file_path = "/tmp/testdir/testfile.txt"
        with (
            patch("os.makedirs") as makedirs,
            patch("builtins.open", MagicMock()) as mock_open,
        ):
            _append_file(file_content, file_path)
            makedirs.assert_called_with("/tmp/testdir", exist_ok=True)
            mock_open.assert_called_with(file_path, "a", encoding="utf-8")
            handle = mock_open.return_value.__enter__.return_value
            handle.write.assert_called_with(file_content)

    def test_write_file(self):
        file_content = "Hello, world!"
        file_path = "/tmp/testdir/testfile.txt"
        with (
            patch("os.makedirs") as makedirs,
            patch("builtins.open", MagicMock()) as mock_open,
        ):
            _write_file(file_content, file_path)
            makedirs.assert_called_with("/tmp/testdir", exist_ok=True)
            mock_open.assert_called_with(file_path, "w", encoding="utf-8")
            handle = mock_open.return_value.__enter__.return_value
            handle.write.assert_called_with(file_content)
