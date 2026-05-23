from textual.widgets import Static

from ..strings import _


class AppHeader(Static):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            _("Welcome aboard to Python Perú"),
            id="app-header",
            **kwargs,
        )


class AppFooter(Static):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            _("Proudly built with ❤️ in Perú"),
            id="app-footer",
            **kwargs,
        )
