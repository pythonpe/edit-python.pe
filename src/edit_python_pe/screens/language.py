from pathlib import Path

from babel import Locale
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, OptionList, Static

from ..components.layout import AppFooter, AppHeader
from ..strings import _, set_language
from .auth import AuthScreen
from .quit_confirm import QuitConfirmScreen


def get_available_languages() -> dict[int, str]:
    locales_dir = Path(__file__).parent.parent / "locale"
    langs = ["en"]
    if locales_dir.exists():
        for item in sorted(locales_dir.iterdir()):
            if item.is_dir() and (
                (item / "LC_MESSAGES" / "messages.mo").exists()
                or (item / "LC_MESSAGES" / "messages.po").exists()
            ):
                langs.append(item.name)

    unique_langs = []
    for lang in langs:
        if lang not in unique_langs:
            unique_langs.append(lang)

    return dict(enumerate(unique_langs))


class LanguageScreen(Screen):
    def compose(self) -> ComposeResult:
        self.lang_map = get_available_languages()
        options = []
        for _idx, lang_code in self.lang_map.items():
            try:
                from babel.core import UnknownLocaleError

                name = Locale(lang_code).get_display_name(lang_code)
                display = str(name or lang_code).title()
            except (UnknownLocaleError, ValueError):
                display = lang_code

            options.append(display)

        yield AppHeader()
        with Vertical(id="lang-container"):
            yield Static(_("Select your language"), id="lang-label")
            yield OptionList(
                *options,
                id="lang-select",
            )
            with Horizontal(id="lang-actions"):
                yield Button(_("Continue"), id="lang-continue", variant="primary")
                yield Button(_("Quit"), id="lang-quit", variant="error")
        yield AppFooter()

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        lang_code = (
            self.lang_map.get(event.option_index, "en")
            if getattr(self, "lang_map", None) and event.option_index is not None
            else "en"
        )

        set_language(lang_code)

        # Update labels dynamically
        self.query_one("#app-header", Static).update(_("Welcome aboard to Python Perú"))
        self.query_one("#lang-label", Static).update(_("Select your language"))
        self.query_one("#lang-continue", Button).label = _("Continue")
        self.query_one("#lang-quit", Button).label = _("Quit")
        self.query_one("#app-footer", Static).update(_("Proudly built with ❤️ in Perú"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "lang-quit":

            def check_quit(quit_app: bool | None) -> None:
                if quit_app:
                    self.app.exit()

            self.app.push_screen(QuitConfirmScreen(), check_quit)
        elif event.button.id == "lang-continue":
            # If the user clicks continue without highlighting an option,
            # make sure we set default
            opt_list = self.query_one("#lang-select", OptionList)
            selected_idx = opt_list.highlighted
            lang_code = (
                self.lang_map.get(selected_idx, "en")
                if getattr(self, "lang_map", None) and selected_idx is not None
                else "en"
            )
            set_language(lang_code)
            self.app.push_screen(AuthScreen())
