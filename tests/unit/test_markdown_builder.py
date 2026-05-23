from unittest.mock import patch

from edit_python_pe.markdown_builder import (
    _compute_file_name,
    _create_member_file,
)


class TestMarkdownBuilder:
    def test_create_member_file(self):
        file_content = "Sample member content"
        current_file = None
        repo_path = "/fake/repo"
        aliases = ["alias1"]
        name = "Test Name"
        email = "test@email.com"
        expected_filename_prefix = "alias1-"
        with patch("edit_python_pe.markdown_builder._write_file") as mock_write_file:
            name_file, file_path = _create_member_file(
                file_content, current_file, repo_path, aliases, name, email
            )
            mock_write_file.assert_called_once_with(file_content, file_path)
            assert name_file.startswith(expected_filename_prefix)
            assert name_file.endswith(".md")
            import os

            assert os.path.join("blog", "members") in file_path
            assert file_path.endswith(name_file)

        # Test with current_file provided
        current_file = "existing.md"
        with patch("edit_python_pe.markdown_builder._write_file") as mock_write_file:
            name_file, file_path = _create_member_file(
                file_content, current_file, repo_path, aliases, name, email
            )
            assert name_file == current_file
            assert file_path.endswith(current_file)
            mock_write_file.assert_called_once_with(file_content, file_path)

    def test_compute_file_name_alias_used(self):
        aliases = ["CoolAlias"]
        name = "John Doe"
        email = "john@example.com"
        filename = _compute_file_name(aliases, name, email)
        assert filename.startswith("coolalias-")
        assert filename.endswith(".md")
        assert "-" in filename
        assert filename.count("-") == 1

    def test_compute_file_name_name_used_if_no_alias(self):
        aliases = []
        name = "Jane Doe"
        email = "jane@example.com"
        filename = _compute_file_name(aliases, name, email)
        assert filename.startswith("jane_doe-")
        assert filename.endswith(".md")

    def test_compute_file_name_uniqueness(self):
        aliases = ["Alias"]
        name = "Name"
        email1 = "email1@example.com"
        email2 = "email2@example.com"
        filename1 = _compute_file_name(aliases, name, email1)
        filename2 = _compute_file_name(aliases, name, email2)
        assert filename1 != filename2
