from textual.containers import Horizontal
from textual.widgets import Button, Input

from ..strings import _
from .form_control import FormControl


class AliasEntry(FormControl):
    def __init__(self, index: int) -> None:
        self.index = index
        self.alias_input = Input(placeholder=_("Alias"))
        self.delete_btn = Button(
            _("Delete"), id=f"delete_alias_{index}", variant="error"
        )
        super().__init__(
            Horizontal(self.alias_input, self.delete_btn, classes="entry-row")
        )
