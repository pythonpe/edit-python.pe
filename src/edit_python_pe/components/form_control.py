from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static


class FormControl(Vertical):
    def __init__(
        self,
        *children: Widget,
        label: str = "",
        help_text: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.label_text = label
        self.help_text_content = help_text
        self.children_widgets = children

    def compose(self) -> ComposeResult:
        if self.label_text:
            yield Static(self.label_text, classes="form-label")

        yield from self.children_widgets

        if self.help_text_content:
            yield Static(self.help_text_content, classes="form-help-text")

        yield Static("", classes="form-error-text")

    def on_mount(self) -> None:
        self.query_one(".form-error-text", Static).display = False

    def show_error(self, message: str) -> None:
        error_static = self.query_one(".form-error-text", Static)
        error_static.update(message)
        error_static.display = True

        # Apply has-error class to self
        self.add_class("has-error")

    def clear_error(self) -> None:
        error_static = self.query_one(".form-error-text", Static)
        error_static.update("")
        error_static.display = False

        # Remove has-error class from self
        self.remove_class("has-error")
