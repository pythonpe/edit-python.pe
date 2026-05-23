from unittest.mock import patch

import pytest

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.auth import AuthScreen
from edit_python_pe.screens.language import LanguageScreen
from edit_python_pe.screens.quit_confirm import QuitConfirmScreen


class TestLanguageScreen:
    @pytest.mark.asyncio
    async def test_language_screen(self):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(LanguageScreen())
            await pilot.pause()
            await pilot.click("#lang-continue")
            await pilot.pause()
            assert isinstance(app.screen, AuthScreen)

    @pytest.mark.asyncio
    async def test_language_screen_es(self):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(LanguageScreen())
            await pilot.pause()
            await pilot.press("down")
            await pilot.click("#lang-continue")
            await pilot.pause()
            assert isinstance(app.screen, AuthScreen)

    @pytest.mark.asyncio
    async def test_language_screen_quit(self):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(LanguageScreen())
            await pilot.pause()
            await pilot.click("#lang-quit")
            await pilot.pause()
            assert isinstance(app.screen, QuitConfirmScreen)
            with patch.object(app, "exit") as mock_exit:
                await pilot.click("#quit-confirm-close")
                await pilot.pause()
                mock_exit.assert_called_once()
