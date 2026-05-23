from github.Repository import Repository
from textual.app import App

from .screens.language import LanguageScreen


class MemberApp(App):
    CSS_PATH = "styles.tcss"

    def __init__(self) -> None:
        super().__init__()
        self.original_repo: Repository | None = None
        self.forked_repo: Repository | None = None
        self.token: str | None = None
        self.repo_path: str | None = None

    def on_mount(self) -> None:
        self.push_screen(LanguageScreen())
