import logging

import keyring
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from ..components.layout import AppFooter, AppHeader
from ..strings import _
from .loading import LoadingScreen
from .quit_confirm import QuitConfirmScreen

logger = logging.getLogger(__name__)


class AuthScreen(Screen):
    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Vertical(id="auth-container"):
            yield Static(_("Please enter your GitHub personal access token: "))
            yield Input(password=True, id="github-token")
            with Horizontal(id="auth-actions"):
                with Horizontal(id="auth-actions-left"):
                    yield Button(_("Login"), id="login-btn", variant="primary")
                with Horizontal(id="auth-actions-right"):
                    yield Button(_("Back"), id="auth-back")
                    yield Button(_("Quit"), id="auth-quit", variant="error")
        yield AppFooter()

    def on_mount(self) -> None:
        try:
            token = keyring.get_password("edit-python-pe", "github_token")
            if token:
                self.query_one("#github-token", Input).value = token
        except Exception:
            logger.error("Failed to retrieve token from keyring", exc_info=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-btn":
            token = self.query_one("#github-token", Input).value.strip()
            if not token:
                return

            try:
                keyring.set_password("edit-python-pe", "github_token", token)
            except Exception:
                logger.error("Failed to save token to keyring", exc_info=True)

            self.app.push_screen(LoadingScreen(token))
        elif event.button.id == "auth-quit":

            def check_quit(quit_app: bool | None) -> None:
                if quit_app:
                    self.app.exit()

            self.app.push_screen(QuitConfirmScreen(), check_quit)
        elif event.button.id == "auth-back":
            self.app.pop_screen()
