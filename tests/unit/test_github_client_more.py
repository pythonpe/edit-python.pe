from unittest.mock import MagicMock, patch

from edit_python_pe.github_client import create_pr


class TestGithubClientMore:
    @patch("edit_python_pe.github_client._create_member_file")
    @patch("edit_python_pe.github_client._write_authors_file")
    @patch("edit_python_pe.github_client._commit_and_push")
    @patch("edit_python_pe.github_client.Github")
    def test_save_member_with_current_file_and_existing_pr(
        self,
        mock_github_class,
        mock_commit_and_push,
        mock_write_authors,
        mock_create_member_file,
    ):
        # Setup mocks
        mock_create_member_file.return_value = (
            "test.md",
            "/fake/path/test.md",
        )
        mock_repo = MagicMock()
        mock_remote = MagicMock()
        mock_callbacks = MagicMock()
        mock_commit_and_push.return_value = (
            "Commit MSG",
            mock_repo,
            mock_remote,
            mock_callbacks,
        )

        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        mock_github.get_user.return_value.login = "testuser"

        mock_original_repo = MagicMock()
        mock_forked_repo = MagicMock()

        mock_pr = MagicMock()
        mock_pr.title = "Update test.md"
        mock_pr.html_url = "http://fake-pr-url"
        mock_original_repo.get_pulls.return_value = [mock_pr]

        msg, url = create_pr(
            file_content="test",
            current_file="test.md",
            repo_path="/fake/repo",
            original_repo=mock_original_repo,
            forked_repo=mock_forked_repo,
            token="faketoken",
            aliases=[],
            name="Test Name",
            email="test@email.com",
        )

        assert url == "http://fake-pr-url"
        assert "existing PR" in msg
        mock_remote.push.assert_called_once()

    @patch("edit_python_pe.github_client._create_member_file")
    @patch("edit_python_pe.github_client._write_authors_file")
    @patch("edit_python_pe.github_client._commit_and_push")
    @patch("edit_python_pe.github_client.Github")
    def test_save_member_with_current_file_no_existing_pr(
        self,
        mock_github_class,
        mock_commit_and_push,
        mock_write_authors,
        mock_create_member_file,
    ):
        # Setup mocks
        mock_create_member_file.return_value = (
            "test.md",
            "/fake/path/test.md",
        )
        mock_repo = MagicMock()
        mock_remote = MagicMock()
        mock_callbacks = MagicMock()
        mock_commit_and_push.return_value = (
            "Commit MSG",
            mock_repo,
            mock_remote,
            mock_callbacks,
        )

        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        mock_github.get_user.return_value.login = "testuser"

        mock_original_repo = MagicMock()
        mock_forked_repo = MagicMock()

        mock_original_repo.get_pulls.return_value = []
        mock_pr = MagicMock()
        mock_pr.html_url = "http://fake-pr-url-new"
        mock_original_repo.create_pull.return_value = mock_pr

        _, url = create_pr(
            file_content="test",
            current_file="test.md",
            repo_path="/fake/repo",
            original_repo=mock_original_repo,
            forked_repo=mock_forked_repo,
            token="faketoken",
            aliases=[],
            name="Test Name",
            email="test@email.com",
        )

        assert url == "http://fake-pr-url-new"
        mock_original_repo.create_pull.assert_called_once()
