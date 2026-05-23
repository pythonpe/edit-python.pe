from unittest.mock import patch

import pytest
from textual.widgets import OptionList

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.language import LanguageScreen
from edit_python_pe.screens.member_form import (
    MemberFormScreen,
)
from edit_python_pe.screens.member_list import MemberListScreen


class TestMemberListScreen:
    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.member_list.os.path.exists")
    @patch("edit_python_pe.screens.member_list.glob.glob")
    async def test_member_list_screen(self, mock_glob, mock_exists):
        mock_exists.return_value = True
        mock_glob.return_value = ["path/file1.md", "path/file2.md"]
        app = MemberApp()
        app.repo_path = "path"
        async with app.run_test() as pilot:
            await app.push_screen(MemberListScreen())
            await pilot.pause()
            option_list = app.screen.query_one("#member-list-view", OptionList)
            assert option_list.option_count == 2

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.member_list.os.path.exists")
    async def test_member_list_screen_no_dir(self, mock_exists):
        mock_exists.return_value = False
        app = MemberApp()
        app.repo_path = "path"
        async with app.run_test() as pilot:
            await app.push_screen(MemberListScreen())
            await pilot.pause()
            assert isinstance(app.screen, MemberListScreen)

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.member_list.os.path.exists")
    @patch("edit_python_pe.screens.member_list.glob.glob")
    async def test_member_list_screen_edit(self, mock_glob, mock_exists):
        mock_exists.return_value = True
        mock_glob.return_value = ["path/file1.md", "path/file2.md"]
        app = MemberApp()
        app.repo_path = "path"
        async with app.run_test() as pilot:
            await app.push_screen(MemberListScreen())
            await pilot.pause()

            # Test selecting an item to edit
            opt_list = app.screen.query_one("#member-list-view", OptionList)
            opt_list.highlighted = 0
            await pilot.click("#member-list-edit")
            await pilot.pause()

            assert isinstance(app.screen, MemberFormScreen)
            assert app.screen.current_file == "file1.md"

    @pytest.mark.asyncio
    async def test_member_list_screen_quit_confirm(self):
        app = MemberApp()
        app.repo_path = "path"
        async with app.run_test() as pilot:
            await app.push_screen(MemberListScreen())
            await pilot.pause()
            await pilot.click("#member-list-back")
            await pilot.pause()
            assert isinstance(app.screen, LanguageScreen)
