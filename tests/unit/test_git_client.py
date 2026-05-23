from unittest.mock import MagicMock, call, patch

from edit_python_pe.git_client import _commit_and_push


class TestGitClient:
    def test_commit_and_push(self):
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
                patch("pygit2.callbacks.RemoteCallbacks") as RemoteCallbacksMock,
            ):
                SignatureMock.return_value = MagicMock()
                RemoteCallbacksMock.return_value = MagicMock()
                commit_msg, _repo, _remote, _callbacks = _commit_and_push(
                    repo_path,
                    token,
                    was_changed,
                    name_file,
                    name,
                    email,
                )

                repo_instance.index.add.assert_has_calls(
                    [call(f"blog/members/{name_file}"), call("AUTHORS")], any_order=True
                )
                repo_instance.index.write.assert_called()
                repo_instance.create_commit.assert_called()
                repo_instance.remotes["origin"].push.assert_called()
                assert commit_msg == f"Changed {name_file}"
