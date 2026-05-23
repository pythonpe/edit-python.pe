from unittest.mock import MagicMock, patch

import pytest

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.quit_confirm import QuitConfirmScreen
from edit_python_pe.screens.save_loading import SaveLoadingScreen


class TestSaveLoadingScreen:
    @pytest.fixture
    def mock_save_params(self):
        return {
            "file_content": "test",
            "current_file": None,
            "repo_path": "/test/path",
            "original_repo": MagicMock(),
            "forked_repo": MagicMock(),
            "token": "token",
            "aliases": [],
            "name": "Joe",
            "email": "joe@test.com",
        }

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.save_loading.create_pr")
    async def test_save_loading_success(self, mock_create, mock_save_params):
        mock_create.return_value = ("Success!", "http://pr.url")
        app = MemberApp()
        async with app.run_test() as pilot:
            screen = SaveLoadingScreen(**mock_save_params)
            await app.push_screen(screen)

            # Wait for worker to finish
            for _ in range(40):
                await pilot.pause(0.1)
                if app.screen.query_one("#loading-actions").display:
                    break

            assert app.screen.query_one("#loading-actions").display is True
            assert "Success!" in str(app.screen.query_one("#result-msg").render())

            # Test copy URL button
            with patch.object(app, "copy_to_clipboard") as mock_copy:
                await pilot.click("#btn-copy-url")
                await pilot.pause()
                mock_copy.assert_called_with("http://pr.url")

            # Test open PR button
            with patch("webbrowser.open") as mock_open:
                await pilot.click("#btn-open-pr")
                await pilot.pause()
                mock_open.assert_called_with("http://pr.url")

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.save_loading.create_pr")
    async def test_save_loading_success_no_url(self, mock_create, mock_save_params):
        mock_create.return_value = ("Success no URL!", None)
        app = MemberApp()
        async with app.run_test() as pilot:
            screen = SaveLoadingScreen(**mock_save_params)
            await app.push_screen(screen)

            for _ in range(40):
                await pilot.pause(0.1)
                if app.screen.query_one("#loading-actions").display:
                    break

            assert "Success no URL!" in str(
                app.screen.query_one("#result-msg").render()
            )
            assert app.screen.query_one("#pr-url").display is False
            assert app.screen.query_one("#btn-open-pr").display is False

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.save_loading.create_pr")
    async def test_save_loading_error(self, mock_create, mock_save_params):
        mock_create.side_effect = ValueError("Some error")
        app = MemberApp()
        async with app.run_test() as pilot:
            screen = SaveLoadingScreen(**mock_save_params)
            await app.push_screen(screen)

            for _ in range(40):
                await pilot.pause(0.1)
                if app.screen.query_one("#loading-actions").display:
                    break

            assert app.screen.query_one("#loading-actions").display is True
            assert "An error occurred while" in str(
                app.screen.query_one("#result-msg").render()
            )

            # Back button should be visible and work
            await pilot.click("#btn-back")
            await pilot.pause()

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.save_loading.create_pr")
    async def test_save_loading_github_error(self, mock_create, mock_save_params):
        from github import GithubException

        mock_create.side_effect = GithubException(
            401,
            {
                "message": "Bad token",
                "errors": [{"message": "Specific auth error"}],
            },
        )
        app = MemberApp()
        async with app.run_test() as pilot:
            screen = SaveLoadingScreen(**mock_save_params)
            await app.push_screen(screen)

            for _ in range(40):
                await pilot.pause(0.1)
                if app.screen.query_one("#loading-actions").display:
                    break

            assert "An error occurred while" in str(
                app.screen.query_one("#result-msg").render()
            )

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.save_loading.create_pr")
    async def test_save_loading_quit(self, mock_create, mock_save_params):
        mock_create.return_value = ("Success!", "http://pr.url")
        app = MemberApp()
        async with app.run_test() as pilot:
            screen = SaveLoadingScreen(**mock_save_params)
            await app.push_screen(screen)

            for _ in range(40):
                await pilot.pause(0.1)
                if app.screen.query_one("#loading-actions").display:
                    break

            await pilot.click("#btn-quit")
            await pilot.pause()
            assert isinstance(app.screen, QuitConfirmScreen)
            with patch.object(app, "exit") as mock_exit:
                await pilot.click("#quit-confirm-close")
                await pilot.pause()
                mock_exit.assert_called_once()
