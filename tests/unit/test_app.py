import pytest

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.language import LanguageScreen


class TestMemberApp:
    @pytest.mark.asyncio
    async def test_app_mounts_language_screen(self):
        app = MemberApp()
        async with app.run_test():
            # After mounting, the current screen should be LanguageScreen
            assert isinstance(app.screen, LanguageScreen)
