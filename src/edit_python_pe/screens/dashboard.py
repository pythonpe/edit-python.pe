from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button

from ..components.layout import AppFooter, AppHeader
from ..strings import _
from .member_form import MemberFormScreen
from .member_list import MemberListScreen
from .quit_confirm import QuitConfirmScreen


class DashboardScreen(Screen):
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Vertical(id="dashboard-container"):
            yield Button(_("Add New Member"), id="dash-add", variant="success")
            yield Button(_("Edit Existing Member"), id="dash-edit", variant="primary")
            yield Button(_("Quit"), id="dash-quit", variant="error")
        yield AppFooter()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dash-add":
            self.app.push_screen(MemberFormScreen())
        elif event.button.id == "dash-edit":
            self.app.push_screen(MemberListScreen())
        elif event.button.id == "dash-quit":
            self.action_quit_app()

    def action_quit_app(self) -> None:
        def check_quit(quit_app: bool | None) -> None:
            if quit_app:
                self.app.exit(message=_("See you next time!"))

        self.app.push_screen(QuitConfirmScreen(), check_quit)
