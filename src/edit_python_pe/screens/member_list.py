import glob
import os
from typing import TYPE_CHECKING, cast

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, OptionList, Static

if TYPE_CHECKING:
    from ..app import MemberApp

from ..components.layout import AppFooter, AppHeader
from ..strings import _
from .member_form import MemberFormScreen
from .quit_confirm import QuitConfirmScreen


class MemberListScreen(Screen):
    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Vertical(id="member-list-container"):
            yield Static(_("Select a member to edit:"))
            yield OptionList(id="member-list-view")
            with Horizontal(id="member-list-actions"):
                with Horizontal(id="member-list-actions-left"):
                    yield Button(_("Edit"), id="member-list-edit", variant="primary")
                with Horizontal(id="member-list-actions-right"):
                    yield Button(_("Back"), id="member-list-back")
                    yield Button(_("Quit"), id="member-list-quit", variant="error")
        yield AppFooter()

    def on_mount(self) -> None:

        app = cast("MemberApp", self.app)
        if app.repo_path is None:
            return

        md_files = sorted(
            glob.glob(os.path.join(app.repo_path, "blog", "members", "*.md"))
        )
        options = []
        for f in md_files:
            basename = os.path.basename(f)
            options.append(basename)

        opt_list = self.query_one("#member-list-view", OptionList)
        opt_list.clear_options()
        opt_list.add_options(options)

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        # Do nothing on select, wait for explicit Edit button click
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "member-list-back":
            self.app.pop_screen()
        elif event.button.id == "member-list-quit":

            def check_quit(quit_app: bool | None) -> None:
                if quit_app:
                    self.app.exit()

            self.app.push_screen(QuitConfirmScreen(), check_quit)
        elif event.button.id == "member-list-edit":
            opt_list = self.query_one("#member-list-view", OptionList)
            if opt_list.highlighted is not None:
                filename = str(
                    opt_list.get_option_at_index(opt_list.highlighted).prompt
                )
                self.app.push_screen(MemberFormScreen(filename=filename))
