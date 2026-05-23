import pytest

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.quit_confirm import QuitConfirmScreen


class TestQuitConfirmScreen:
    @pytest.mark.asyncio
    async def test_quit_confirm_screen(self):
        app = MemberApp()
        async with app.run_test() as pilot:
            await app.push_screen(QuitConfirmScreen())
            await pilot.pause()
            await pilot.click("#quit-confirm-cancel")
            await pilot.pause()
            # Returns back to whatever was under it
            assert len(app.screen_stack) == 2
