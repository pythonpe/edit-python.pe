from unittest.mock import patch

import pytest
from textual.widgets import Input

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.auth import AuthScreen
from edit_python_pe.screens.dashboard import DashboardScreen
from edit_python_pe.screens.loading import LoadingScreen
from edit_python_pe.screens.quit_confirm import QuitConfirmScreen


class TestAuthScreen:
    @pytest.mark.asyncio
    @patch("keyring.get_password", return_value="saved-token")
    async def test_auth_screen_with_saved_token(self, mock_get):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(AuthScreen())
            await pilot.pause()

            token_input = app.screen.query_one("#github-token", Input)
            assert token_input.value == "saved-token"

    @pytest.mark.asyncio
    @patch("keyring.get_password", return_value=None)
    @patch("keyring.set_password")
    async def test_auth_screen_no_saved_token(self, mock_set, mock_get):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(AuthScreen())
            await pilot.pause()

            # Empty input shouldn't login
            await pilot.click("#login-btn")
            await pilot.pause()
            assert isinstance(app.screen, AuthScreen)

            # Enter token
            await pilot.click("#github-token")
            await pilot.press("t", "e", "s", "t")
            await pilot.pause()
            await pilot.click("#login-btn")
            await pilot.pause()

            mock_set.assert_called_with("edit-python-pe", "github_token", "test")
            assert isinstance(app.screen, LoadingScreen)
            assert app.screen.token == "test"

    @pytest.mark.asyncio
    @patch("keyring.get_password", side_effect=Exception("mocked"))
    @patch("keyring.set_password", side_effect=Exception("mocked"))
    async def test_auth_screen_exceptions(self, mock_set, mock_get):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(AuthScreen())
            await pilot.pause()
            # Should catch exceptions silently
            await pilot.click("#github-token")
            await pilot.press("x")
            await pilot.pause()
            await pilot.click("#login-btn")
            await pilot.pause()
            assert isinstance(app.screen, LoadingScreen)

    @pytest.mark.asyncio
    async def test_auth_screen_back(self):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(DashboardScreen())
            await app.push_screen(AuthScreen())
            await pilot.pause()
            await pilot.click("#auth-back")
            await pilot.pause()
            assert isinstance(app.screen, DashboardScreen)

    @pytest.mark.asyncio
    async def test_auth_screen_quit(self):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(AuthScreen())
            await pilot.pause()
            # Click quit should push quit confirm screen
            await pilot.click("#auth-quit")
            await pilot.pause()
            assert isinstance(app.screen, QuitConfirmScreen)
            with patch.object(app, "exit") as mock_exit:
                await pilot.click("#quit-confirm-close")
                await pilot.pause()
                mock_exit.assert_called_once()
