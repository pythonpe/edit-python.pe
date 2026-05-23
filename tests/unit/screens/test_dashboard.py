import pytest

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.dashboard import DashboardScreen
from edit_python_pe.screens.member_form import (
    MemberFormScreen,
)
from edit_python_pe.screens.member_list import MemberListScreen
from edit_python_pe.screens.quit_confirm import QuitConfirmScreen


class TestDashboardScreen:
    @pytest.mark.asyncio
    async def test_dashboard_screen_add(self):
        app = MemberApp()
        app.token = "test"
        app.repo_path = "path"
        async with app.run_test() as pilot:
            await app.push_screen(DashboardScreen())
            await pilot.pause()
            await pilot.click("#dash-add")
            await pilot.pause()
            assert isinstance(app.screen, MemberFormScreen)
            assert app.screen.current_file is None

    @pytest.mark.asyncio
    async def test_dashboard_screen_edit(self):
        app = MemberApp()
        app.token = "test"
        app.repo_path = "path"
        async with app.run_test() as pilot:
            await app.push_screen(DashboardScreen())
            await pilot.pause()
            await pilot.click("#dash-edit")
            await pilot.pause()
            assert isinstance(app.screen, MemberListScreen)

    @pytest.mark.asyncio
    async def test_dashboard_screen_quit(self):
        app = MemberApp()
        app.token = "test"
        app.repo_path = "path"
        async with app.run_test() as pilot:
            await app.push_screen(DashboardScreen())
            await pilot.pause()
            await pilot.click("#dash-quit")
            await pilot.pause()
            assert isinstance(app.screen, QuitConfirmScreen)
