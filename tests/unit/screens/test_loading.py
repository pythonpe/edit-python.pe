from unittest.mock import MagicMock, patch

import pytest

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.dashboard import DashboardScreen
from edit_python_pe.screens.loading import LoadingScreen
from edit_python_pe.screens.quit_confirm import QuitConfirmScreen


class TestLoadingScreen:
    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.loading.get_repo")
    @patch("edit_python_pe.screens.loading.fork_repo")
    async def test_loading_screen_success(self, mock_fork, mock_get):
        mock_get.return_value = ("token", MagicMock())
        mock_fork.return_value = ("path", MagicMock())
        app = MemberApp()
        app.token = "test"
        async with app.run_test() as pilot:
            await app.push_screen(LoadingScreen("token"))
            # Wait up to 2 seconds for worker to finish
            for _ in range(20):
                await pilot.pause(0.1)
                if isinstance(app.screen, DashboardScreen):
                    break
            assert isinstance(app.screen, DashboardScreen)
            assert app.repo_path == "path"

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.loading.get_repo")
    async def test_loading_screen_error(self, mock_get):
        mock_get.side_effect = ValueError("Auth Error")
        app = MemberApp()
        app.token = "test"
        async with app.run_test() as pilot:
            await app.push_screen(LoadingScreen("token"))
            # Wait up to 4 seconds
            for _ in range(40):
                await pilot.pause(0.1)
                if app.screen.query_one("#loading-actions").display:
                    break
            assert app.screen.query_one("#loading-actions").display is True
            assert "An unexpected error" in str(
                app.screen.query_one("#result-msg").render()
            )

            # Test loading-back
            await pilot.click("#loading-back")
            await pilot.pause()
            # Popped screen
            from edit_python_pe.screens.language import LanguageScreen

            assert isinstance(app.screen, LanguageScreen)

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.loading.get_repo")
    async def test_loading_screen_quit(self, mock_get):
        mock_get.side_effect = ValueError("Auth Error")
        app = MemberApp()
        app.token = "test"
        async with app.run_test() as pilot:
            await app.push_screen(LoadingScreen("token"))
            for _ in range(40):
                await pilot.pause(0.1)
                if app.screen.query_one("#loading-actions").display:
                    break
            await pilot.click("#loading-quit")
            await pilot.pause()
            assert isinstance(app.screen, QuitConfirmScreen)
            with patch.object(app, "exit") as mock_exit:
                await pilot.click("#quit-confirm-close")
                await pilot.pause()
                mock_exit.assert_called_once()
