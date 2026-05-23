import logging
from typing import TYPE_CHECKING, cast

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, LoadingIndicator, Static

if TYPE_CHECKING:
    from ..app import MemberApp

from ..components.layout import AppFooter, AppHeader
from ..github_client import fork_repo, get_repo
from ..strings import _
from .dashboard import DashboardScreen
from .quit_confirm import QuitConfirmScreen

logger = logging.getLogger(__name__)


class LoadingScreen(Screen):
    def __init__(self, token: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.token = token

    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Vertical(id="loading-container"):
            yield LoadingIndicator(id="loading-anim")
            yield Static(
                _("Authenticating and fetching repository..."),
                id="loading-msg",
            )

            with Vertical(id="loading-result-container"):
                yield Static("", id="result-icon")
                yield Static("", id="result-msg")

            with Horizontal(id="loading-actions"):
                yield Button(_("Back"), id="loading-back")
                yield Button(_("Quit"), id="loading-quit", variant="error")
        yield AppFooter()

    def on_mount(self) -> None:
        self.query_one("#loading-result-container").display = False
        self.query_one("#loading-actions").display = False
        self.authenticate_and_clone()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "loading-quit":

            def check_quit(quit_app: bool | None) -> None:
                if quit_app:
                    self.app.exit()

            self.app.push_screen(QuitConfirmScreen(), check_quit)
        elif event.button.id == "loading-back":
            self.app.pop_screen()

    @work(thread=True, exclusive=True)
    def authenticate_and_clone(self) -> None:
        try:
            _token, original_repo = get_repo(self.token)
            repo_path, forked_repo = fork_repo(self.token, original_repo)

            app = cast("MemberApp", self.app)

            app.original_repo = original_repo
            app.forked_repo = forked_repo
            app.repo_path = repo_path
            app.token = self.token

            self.app.call_from_thread(self.show_success)
        except Exception:
            logger.error("Error during authentication and cloning", exc_info=True)
            error_message = _(
                "An unexpected error occurred while loading. "
                "Please try again or contact support."
            )
            self.app.call_from_thread(self.show_error, error_message)

    def show_success(self) -> None:
        self.query_one("#loading-anim").display = False
        self.query_one("#loading-msg").display = False

        result_container = self.query_one("#loading-result-container")
        result_container.display = True

        icon = self.query_one("#result-icon", Static)
        icon.update("✅")
        icon.add_class("success-icon")

        msg = self.query_one("#result-msg", Static)
        msg.update(_("Successfully authenticated!"))

        self.set_timer(1.5, self.advance_screen)

    def advance_screen(self) -> None:
        self.app.push_screen(DashboardScreen())

    def show_error(self, error_message: str) -> None:
        self.query_one("#loading-anim").display = False
        self.query_one("#loading-msg").display = False

        result_container = self.query_one("#loading-result-container")
        result_container.display = True

        icon = self.query_one("#result-icon", Static)
        icon.update("✘")
        icon.add_class("error-icon")

        msg = self.query_one("#result-msg", Static)
        msg.update(error_message)
        msg.add_class("error-text")

        self.query_one("#loading-actions").display = True
