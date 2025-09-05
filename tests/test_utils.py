import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)
from edit_python_pe.utils import fork_repo, get_repo


class TestUtilityFunctions(unittest.TestCase):
    def test_create_member_file(self):
        from unittest.mock import patch

        from edit_python_pe.utils import _create_member_file

        file_content = "Sample member content"
        current_file = None
        repo_path = "/fake/repo"
        aliases = ["alias1"]
        name = "Test Name"
        email = "test@email.com"
        expected_filename_prefix = "alias1-"
        with patch("edit_python_pe.utils._write_file") as mock_write_file:
            name_file, file_path = _create_member_file(
                file_content, current_file, repo_path, aliases, name, email
            )
            mock_write_file.assert_called_once_with(file_content, file_path)
            self.assertTrue(name_file.startswith(expected_filename_prefix))
            self.assertTrue(name_file.endswith(".md"))
            self.assertIn("blog/members/", file_path)
            self.assertTrue(file_path.endswith(name_file))

        # Test with current_file provided
        current_file = "existing.md"
        with patch("edit_python_pe.utils._write_file") as mock_write_file:
            name_file, file_path = _create_member_file(
                file_content, current_file, repo_path, aliases, name, email
            )
            self.assertEqual(name_file, current_file)
            self.assertTrue(file_path.endswith(current_file))
            mock_write_file.assert_called_once_with(file_content, file_path)

        name = "Test Name"
        email = "test@email.com"

    def test_write_authors_file(self):
        from unittest.mock import patch

        from edit_python_pe.utils import _write_authors_file

        repo_path = "/fake/repo"
        aliases = ["alias1"]
        name = "Test Name"
        email = "test@email.com"
        file_path = f"{repo_path}/AUTHORS"
        # Case: author not present, should append
        with (
            patch(
                "edit_python_pe.utils._read_file", return_value=""
            ) as mock_read_file,
            patch("edit_python_pe.utils._append_file") as mock_append_file,
        ):
            _write_authors_file(repo_path, aliases, name, email)
            mock_read_file.assert_called_once_with(file_path)
            mock_append_file.assert_called_once()
            args, _ = mock_append_file.call_args
            self.assertIn(name, args[0])
            self.assertIn(email, args[0])

        # Case: author already present, should not append
        existing_line = f"\n{name}(alias1) <{email}>"
        with (
            patch(
                "edit_python_pe.utils._read_file", return_value=existing_line
            ) as mock_read_file,
            patch("edit_python_pe.utils._append_file") as mock_append_file,
        ):
            _write_authors_file(repo_path, aliases, name, email)
            mock_read_file.assert_called_once_with(file_path)
            mock_append_file.assert_not_called()

    def test_get_alias(self):
        from edit_python_pe.utils import _get_alias

        # Case: aliases present
        aliases = ["CoolAlias"]
        name = "John Doe"
        self.assertEqual(_get_alias(aliases, name), "CoolAlias")
        # Case: aliases absent
        aliases = []
        self.assertEqual(_get_alias(aliases, name), name)
        # Case: aliases absent
        aliases = []

    def test_read_file(self):
        from edit_python_pe.utils import _read_file

        file_path = "/tmp/testfile.txt"
        expected_content = "Hello, world!"
        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                expected_content
            )
            result = _read_file(file_path)
            mock_open.assert_called_with(file_path, "r", encoding="utf-8")
            self.assertEqual(result, expected_content)

    def test_append_file(self):
        from edit_python_pe.utils import _append_file

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

    def test_compute_file_name_alias_used(self):
        from edit_python_pe.utils import _compute_file_name

        aliases = ["CoolAlias"]
        name = "John Doe"
        email = "john@example.com"
        filename = _compute_file_name(aliases, name, email)
        self.assertTrue(filename.startswith("coolalias-"))
        self.assertTrue(filename.endswith(".md"))
        self.assertIn("-", filename)
        self.assertEqual(filename.count("-"), 1)

    def test_compute_file_name_name_used_if_no_alias(self):
        from edit_python_pe.utils import _compute_file_name

        aliases = []
        name = "Jane Doe"
        email = "jane@example.com"
        filename = _compute_file_name(aliases, name, email)
        self.assertTrue(filename.startswith("jane_doe-"))
        self.assertTrue(filename.endswith(".md"))

    def test_compute_file_name_uniqueness(self):
        from edit_python_pe.utils import _compute_file_name

        aliases = ["Alias"]
        name = "Name"
        email1 = "email1@example.com"
        email2 = "email2@example.com"
        filename1 = _compute_file_name(aliases, name, email1)
        filename2 = _compute_file_name(aliases, name, email2)
        self.assertNotEqual(filename1, filename2)

    def test_write_file(self):

        from edit_python_pe.utils import _write_file

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

    def test_commit_and_push(self):
        from edit_python_pe.utils import _commit_and_push

        repo_path = "/fake/repo"
        token = "fake-token"
        was_changed = True
        name_file = "test.md"
        name = "Test Name"
        email = "test@email.com"
        with patch("pygit2.repository.Repository") as RepoMock:
            repo_instance = RepoMock.return_value
            repo_instance.index.add = MagicMock()
            repo_instance.index.write = MagicMock()
            repo_instance.index.write_tree = MagicMock(return_value="treeid")
            repo_instance.head_is_unborn = False
            repo_instance.head = MagicMock()
            repo_instance.head.target = "commitid"
            repo_instance.create_commit = MagicMock()
            repo_instance.remotes = {"origin": MagicMock()}
            repo_instance.remotes["origin"].push = MagicMock()
            with (
                patch("pygit2.Signature") as SignatureMock,
                patch(
                    "pygit2.callbacks.RemoteCallbacks"
                ) as RemoteCallbacksMock,
            ):
                SignatureMock.return_value = MagicMock()
                RemoteCallbacksMock.return_value = MagicMock()
                commit_msg, repo, remote, callbacks = _commit_and_push(
                    repo_path,
                    token,
                    was_changed,
                    name_file,
                    name,
                    email,
                )
                repo_instance.index.add_all.assert_called()
                repo_instance.index.write.assert_called()
                repo_instance.create_commit.assert_called()
                repo_instance.remotes["origin"].push.assert_called()
                self.assertEqual(commit_msg, f"Changed {name_file}")


class TestGetRepo(unittest.TestCase):
    @patch("edit_python_pe.utils.getpass.getpass", return_value="valid-token")
    @patch("edit_python_pe.utils.Github")
    def test_get_repo_success(self, mock_github, mock_getpass):
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        token, repo = get_repo()
        self.assertEqual(token, "valid-token")
        self.assertEqual(repo, mock_repo)

    @patch(
        "edit_python_pe.utils.getpass.getpass", return_value="invalid-token"
    )
    @patch("edit_python_pe.utils.Github")
    def test_get_repo_bad_credentials(self, mock_github, mock_getpass):
        from github.GithubException import BadCredentialsException

        mock_github.return_value.get_repo.side_effect = (
            BadCredentialsException(401, "Bad credentials", None)
        )
        with self.assertRaises(SystemExit):
            get_repo()

    @patch("edit_python_pe.utils.getpass.getpass", return_value="valid-token")
    @patch("edit_python_pe.utils.Github")
    def test_get_repo_github_exception(self, mock_github, mock_getpass):
        from github.GithubException import GithubException

        mock_github.return_value.get_repo.side_effect = GithubException(
            404, "Not found", None
        )
        with self.assertRaises(SystemExit):
            get_repo()


class TestForkRepo(unittest.TestCase):
    @patch("edit_python_pe.utils.user_data_dir", return_value="/tmp/testrepo")
    @patch("edit_python_pe.utils.os.path.exists", return_value=False)
    @patch("edit_python_pe.utils.pygit2.clone_repository")
    @patch("edit_python_pe.utils.sleep", return_value=None)
    def test_fork_repo_clones_if_not_exists(
        self, mock_sleep, mock_clone, mock_exists, mock_user_data_dir
    ):
        mock_forked_repo = MagicMock()
        mock_forked_repo.clone_url = "https://github.com/fake/fork.git"
        mock_original_repo = MagicMock()
        mock_original_repo.create_fork.return_value = mock_forked_repo
        token = "fake-token"
        repo_path = fork_repo(token, mock_original_repo)[0]
        mock_original_repo.create_fork.assert_called_once()
        mock_clone.assert_called_once()
        call_args = mock_clone.call_args
        self.assertEqual(call_args[0][0], mock_forked_repo.clone_url)
        self.assertEqual(call_args[0][1], repo_path)
        self.assertEqual(repo_path, "/tmp/testrepo")

    @patch("edit_python_pe.utils.user_data_dir", return_value="/tmp/testrepo")
    @patch("edit_python_pe.utils.os.path.exists", return_value=True)
    @patch("edit_python_pe.utils.pygit2.clone_repository")
    def test_fork_repo_no_clone_if_exists(
        self, mock_clone, mock_exists, mock_user_data_dir
    ):
        mock_forked_repo = MagicMock()
        mock_forked_repo.clone_url = "https://github.com/fake/fork.git"
        mock_original_repo = MagicMock()
        mock_original_repo.create_fork.return_value = mock_forked_repo
        token = "fake-token"
        repo_path = fork_repo(token, mock_original_repo)[0]
        mock_original_repo.create_fork.assert_called_once()
        mock_clone.assert_not_called()
        self.assertEqual(repo_path, "/tmp/testrepo")
