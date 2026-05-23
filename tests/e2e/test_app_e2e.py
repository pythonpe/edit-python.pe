import tempfile
from unittest.mock import MagicMock, patch

import pytest

from edit_python_pe.app import MemberApp
from edit_python_pe.screens.auth import AuthScreen
from edit_python_pe.screens.dashboard import DashboardScreen
from edit_python_pe.screens.language import LanguageScreen
from edit_python_pe.screens.member_form import MemberFormScreen
from edit_python_pe.screens.save_loading import SaveLoadingScreen


async def _wait_for_dashboard(pilot, app, max_range=50):
    for _ in range(max_range):
        await pilot.pause(0.1)
        if isinstance(app.screen, DashboardScreen):
            return


async def _wait_for_save_loading_actions(pilot, app, max_range=50):
    for _ in range(max_range):
        await pilot.pause(0.1)
        if (
            isinstance(app.screen, SaveLoadingScreen)
            and app.screen.query("#loading-actions")
            and app.screen.query("#loading-actions").first().display
        ):
            return


async def _wait_for_member_form(pilot, app, max_range=10):
    for _ in range(max_range):
        await pilot.pause(0.1)
        if isinstance(app.screen, MemberFormScreen):
            return


class TestAppE2E:
    @pytest.mark.asyncio
    @patch("edit_python_pe.screens.loading.get_repo")
    @patch("edit_python_pe.screens.loading.fork_repo")
    @patch("edit_python_pe.screens.save_loading.create_pr")
    @patch("keyring.get_password", return_value=None)
    @patch("keyring.set_password")
    async def test_full_app_flow(
        self,
        mock_set_password,
        mock_get_password,
        mock_create_pr,
        mock_fork_repo,
        mock_get_repo_loading,
    ):
        mock_repo = MagicMock()
        mock_forked = MagicMock()
        mock_get_repo_loading.return_value = ("fake-token", mock_repo)
        mock_fork_repo.return_value = (tempfile.gettempdir(), mock_forked)
        mock_create_pr.return_value = (
            "Woohoo! john_doe-abc12345.md was saved successfully and your new PR is ready! 🎉",
            "https://github.com/fake/pr",
        )

        app = MemberApp()
        async with app.run_test(size=(120, 100)) as pilot:
            # 1. Language Screen
            assert isinstance(app.screen, LanguageScreen)
            await pilot.click("#lang-continue")
            await pilot.pause()

            # 2. Auth Screen
            assert isinstance(app.screen, AuthScreen)
            await pilot.click("#github-token")
            await pilot.press("f", "a", "k", "e")
            await pilot.pause()
            await pilot.click("#login-btn")

            # 3. Loading Screen
            # The background thread sets app repos; advance_screen fires after a
            # 1.5 s timer. Give it up to 5 s total to reach DashboardScreen in CI.
            await _wait_for_dashboard(pilot, app)
            assert isinstance(app.screen, DashboardScreen)

            # Verify repos were populated by LoadingScreen before proceeding
            assert app.original_repo is not None
            assert app.forked_repo is not None

            # 4. Dashboard -> Add Member
            from textual.widgets import Button

            app.screen.query_one("#dash-add", Button).press()
            await pilot.pause()
            assert isinstance(app.screen, MemberFormScreen)

            # 5.1 Validation test — call methods directly to avoid OutOfBounds
            # errors on widgets inside the VerticalScroll that may be off-screen.
            screen = app.screen
            assert isinstance(screen, MemberFormScreen)
            screen.add_alias_entry()
            screen.add_social_entry()
            await pilot.pause()

            # Fill with invalid URLs
            screen.homepage_input.value = "not_a_url"
            if screen.social_entries:
                screen.social_entries[-1].url_input.value = "not_a_social_url"
                screen.social_entries[-1].select.value = "github"

            screen.action_save()
            await pilot.pause()

            # Validation should prevent navigating away
            assert isinstance(app.screen, MemberFormScreen)

            # 5. Fill valid data and save
            screen = app.screen
            assert isinstance(screen, MemberFormScreen)
            screen.name_input.value = "John Doe"
            screen.email_input.value = "john@example.com"
            screen.city_input.value = "Lima"
            screen.homepage_input.value = "https://example.com"
            if screen.social_entries:
                screen.social_entries[-1].url_input.value = "https://github.com/john"
                screen.social_entries[-1].select.value = "github"
            if screen.alias_entries:
                screen.alias_entries[-1].alias_input.value = "john-gh"

            await pilot.pause()
            screen.action_save()

            # 6. Save Loading Screen — give up to 5 s for the background work
            await _wait_for_save_loading_actions(pilot, app)
            assert isinstance(app.screen, SaveLoadingScreen)
            assert "was saved successfully" in str(
                app.screen.query_one("#result-msg").render()
            )

            # 7. Back to Dashboard
            app.pop_screen()
            await pilot.pause()
            await _wait_for_member_form(pilot, app)

            # Now we are back at MemberFormScreen
            assert isinstance(app.screen, MemberFormScreen)

            # Click discard to go back to Dashboard
            app.pop_screen()
            await pilot.pause()
            await _wait_for_dashboard(pilot, app, max_range=10)
            assert isinstance(app.screen, DashboardScreen)
