from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.member_form import (
    DiscardConfirmScreen,
    MemberFormScreen,
)
from edit_python_pe.screens.quit_confirm import QuitConfirmScreen


class TestMemberFormScreen:
    @pytest.mark.asyncio
    async def test_member_form_add_buttons(self):
        app = MemberApp()
        app.token = "fake-token"
        app.repo_path = "fake/path"
        app.original_repo = MagicMock()
        app.forked_repo = MagicMock()
        async with app.run_test(size=(120, 100)) as pilot:
            await app.push_screen(MemberFormScreen())
            await pilot.pause()

            # Test add alias
            await pilot.click("#member-form-add-alias")
            await pilot.pause()
            assert len(cast(MemberFormScreen, app.screen).alias_entries) == 1

            # Test add social
            await pilot.click("#member-form-add-social")
            await pilot.pause()
            assert len(cast(MemberFormScreen, app.screen).social_entries) == 1

    @pytest.mark.asyncio
    async def test_member_form_quit_button(self):
        app = MemberApp()
        app.token = "fake-token"
        app.repo_path = "fake/path"
        app.original_repo = MagicMock()
        app.forked_repo = MagicMock()
        async with app.run_test(size=(120, 100)) as pilot:
            await app.push_screen(MemberFormScreen())
            await pilot.pause()
            await pilot.click("#member-form-quit")
            await pilot.pause()
            assert isinstance(app.screen, QuitConfirmScreen)

    @pytest.mark.asyncio
    async def test_member_form_discard_button(self):
        app = MemberApp()
        app.token = "fake-token"
        app.repo_path = "fake/path"
        app.original_repo = MagicMock()
        app.forked_repo = MagicMock()
        async with app.run_test(size=(120, 100)) as pilot:
            await app.push_screen(MemberFormScreen())
            await pilot.pause()
            await pilot.click("#member-form-discard")
            await pilot.pause()
            assert isinstance(app.screen, DiscardConfirmScreen)

    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.member_form.MemberFormScreen.action_save")
    async def test_member_form_save_button(self, mock_save):
        app = MemberApp()
        app.token = "fake-token"
        app.repo_path = "fake/path"
        app.original_repo = MagicMock()
        app.forked_repo = MagicMock()
        async with app.run_test(size=(120, 100)) as pilot:
            await app.push_screen(MemberFormScreen())
            await pilot.pause()
            await pilot.click("#member-form-save")
            await pilot.pause()
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_member_form_delete_social(self):
        app = MemberApp()
        app.token = "fake-token"
        app.repo_path = "fake/path"
        app.original_repo = MagicMock()
        app.forked_repo = MagicMock()
        async with app.run_test(size=(120, 100)) as pilot:
            await app.push_screen(MemberFormScreen())
            await pilot.pause()
            await pilot.click("#member-form-add-social")
            await pilot.pause()
            assert len(cast(MemberFormScreen, app.screen).social_entries) == 1

            # Now click delete
            await pilot.click("#delete_social_0")
            await pilot.pause()
            assert len(cast(MemberFormScreen, app.screen).social_entries) == 0

    @pytest.mark.asyncio
    async def test_member_form_delete_alias(self):
        app = MemberApp()
        app.token = "fake-token"
        app.repo_path = "fake/path"
        app.original_repo = MagicMock()
        app.forked_repo = MagicMock()
        async with app.run_test(size=(120, 100)) as pilot:
            await app.push_screen(MemberFormScreen())
            await pilot.pause()
            await pilot.click("#member-form-add-alias")
            await pilot.pause()
            assert len(cast(MemberFormScreen, app.screen).alias_entries) == 1

            # Now click delete
            await pilot.click("#delete_alias_0")
            await pilot.pause()
            assert len(cast(MemberFormScreen, app.screen).alias_entries) == 0

    @pytest.mark.asyncio
    async def test_member_form_invalid_inputs(self):
        app = MemberApp()
        app.token = "fake-token"
        app.repo_path = "fake/path"
        app.original_repo = MagicMock()
        app.forked_repo = MagicMock()
        async with app.run_test(size=(120, 100)) as pilot:
            await app.push_screen(MemberFormScreen())
            await pilot.pause()

            # Insert invalid inputs
            cast(MemberFormScreen, app.screen).name_input.value = "Test"
            cast(MemberFormScreen, app.screen).email_input.value = "invalid-email"
            cast(MemberFormScreen, app.screen).homepage_input.value = "invalid-url"

            await pilot.click("#member-form-add-social")
            await pilot.pause()
            cast(MemberFormScreen, app.screen).social_entries[
                0
            ].url_input.value = "invalid-social"

            await pilot.click("#member-form-save")
            await pilot.pause()

            # Check that errors are shown
            assert cast(MemberFormScreen, app.screen).email_control.has_class(
                "has-error"
            )
            assert cast(MemberFormScreen, app.screen).homepage_control.has_class(
                "has-error"
            )
            assert (
                cast(MemberFormScreen, app.screen)
                .social_entries[0]
                .has_class("has-error")
            )
