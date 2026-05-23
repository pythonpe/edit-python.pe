from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ..strings import _


class QuitConfirmScreen(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        with Vertical(id="quit-confirm-dialog"):
            yield Static(
                _("Are you sure you want to close the app?"),
                id="quit-confirm-dialog-msg",
            )
            with Horizontal(id="quit-confirm-dialog-actions"):
                yield Button(
                    _("Cancel"),
                    id="quit-confirm-cancel",
                    variant="primary",
                )
                yield Button(
                    _("Close"),
                    id="quit-confirm-close",
                    variant="error",
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit-confirm-cancel":
            self.dismiss(False)
        else:
            self.dismiss(True)
