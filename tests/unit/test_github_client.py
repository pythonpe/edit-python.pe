from unittest.mock import MagicMock, patch

import pytest

from edit_python_pe.github_client import fork_repo, get_repo


class TestGithubClient:
    @patch("edit_python_pe.github_client.Github")
    def test_get_repo_success(self, mock_github):
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        token, repo = get_repo("valid-token")
        assert token == "valid-token"
        assert repo == mock_repo

    @patch("edit_python_pe.github_client.Github")
    def test_get_repo_bad_credentials(self, mock_github):
        from github.GithubException import BadCredentialsException

        mock_github.return_value.get_repo.side_effect = BadCredentialsException(
            401, "Bad credentials", None
        )
        with pytest.raises(ValueError):
            get_repo("valid-token")

    @patch("edit_python_pe.github_client.Github")
    def test_get_repo_github_exception(self, mock_github):
        from github.GithubException import GithubException

        mock_github.return_value.get_repo.side_effect = GithubException(
            404, "Not found", None
        )
        with pytest.raises(ValueError):
            get_repo("valid-token")

    @patch(
        "edit_python_pe.github_client.user_data_dir",
        return_value="/tmp/testrepo",
    )
    @patch("edit_python_pe.github_client.os.path.exists", return_value=False)
    @patch("edit_python_pe.github_client.shutil.rmtree")
    @patch("edit_python_pe.github_client.pygit2.clone_repository")
    @patch("edit_python_pe.github_client.sleep", return_value=None)
    def test_fork_repo_no_remove_if_not_exists(
        self,
        mock_sleep,
        mock_clone,
        mock_rmtree,
        mock_exists,
        mock_user_data_dir,
    ):
        mock_forked_repo = MagicMock()
        mock_forked_repo.clone_url = "https://github.com/fake/fork.git"
        mock_original_repo = MagicMock()
        mock_original_repo.create_fork.return_value = mock_forked_repo
        token = "fake-token"
        repo_path = fork_repo(token, mock_original_repo)[0]
        mock_original_repo.create_fork.assert_called_once()
        mock_clone.assert_called_once()
        mock_rmtree.assert_not_called()
        call_args = mock_clone.call_args
        assert call_args[0][0] == mock_forked_repo.clone_url
        assert call_args[0][1] == repo_path
        assert repo_path == "/tmp/testrepo"

    @patch(
        "edit_python_pe.github_client.user_data_dir",
        return_value="/tmp/testrepo",
    )
    @patch("edit_python_pe.github_client.os.path.exists", return_value=True)
    @patch("edit_python_pe.github_client.shutil.rmtree")
    @patch("edit_python_pe.github_client.pygit2.clone_repository")
    @patch("edit_python_pe.github_client.sleep", return_value=None)
    def test_fork_repo_remove_if_exists(
        self,
        mock_sleep,
        mock_clone,
        mock_rmtree,
        mock_exists,
        mock_user_data_dir,
    ):
        mock_forked_repo = MagicMock()
        mock_forked_repo.clone_url = "https://github.com/fake/fork.git"
        mock_original_repo = MagicMock()
        mock_original_repo.create_fork.return_value = mock_forked_repo
        token = "fake-token"
        repo_path = fork_repo(token, mock_original_repo)[0]
        mock_original_repo.create_fork.assert_called_once()
        mock_rmtree.assert_called_once()
        mock_clone.assert_called_once()
        assert repo_path == "/tmp/testrepo"
