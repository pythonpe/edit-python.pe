import logging

from github import GithubException
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, LoadingIndicator, Static

from ..components.layout import AppFooter, AppHeader
from ..github_client import create_pr
from ..strings import _
from .quit_confirm import QuitConfirmScreen

logger = logging.getLogger(__name__)


class SaveLoadingScreen(Screen):
    def __init__(
        self,
        file_content: str,
        current_file: str | None,
        repo_path: str,
        original_repo,
        forked_repo,
        token: str,
        aliases: list[str],
        name: str,
        email: str,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.file_content = file_content
        self.current_file = current_file
        self.repo_path = repo_path
        self.original_repo = original_repo
        self.forked_repo = forked_repo
        self.token = token
        self.aliases = aliases
        self.name_val = name
        self.email_val = email
        self.pr_url: str | None = None

    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Vertical(id="loading-container"):
            yield LoadingIndicator(id="loading-anim")
            yield Static(_("Saving changes and creating PR..."), id="loading-msg")

            with Vertical(id="loading-result-container"):
                yield Static("", id="result-icon")
                yield Static("", id="result-msg")
                yield Static("", id="pr-url")

            with Horizontal(id="loading-actions"):
                yield Button(_("Back"), id="btn-back", variant="primary")
                yield Button(_("Open PR"), id="btn-open-pr", variant="primary")
                yield Button(_("Copy URL"), id="btn-copy-url")
                yield Button(_("Quit"), id="btn-quit", variant="error")
        yield AppFooter()

    def on_mount(self) -> None:
        self.query_one("#loading-result-container").display = False
        self.query_one("#loading-actions").display = False
        self.query_one("#btn-back").display = False
        self.perform_save()

    @work(thread=True, exclusive=True)
    def perform_save(self) -> None:
        try:
            message, pr_url = create_pr(
                self.file_content,
                self.current_file,
                self.repo_path,
                self.original_repo,
                self.forked_repo,
                self.token,
                self.aliases,
                self.name_val,
                self.email_val,
            )
            self.pr_url = pr_url
            self.app.call_from_thread(self.show_success, message)
        except Exception as e:
            github_error_detail = str(e)
            try:
                if isinstance(e, GithubException) and getattr(e, "data", None):
                    errors = e.data.get("errors", [])
                    if errors and isinstance(errors, list):
                        github_error_detail = errors[0].get(
                            "message", e.data.get("message", str(e))
                        )
                    else:
                        github_error_detail = e.data.get("message", str(e))
                logger.error("Error creating PR: %s", github_error_detail, exc_info=e)
            except Exception:
                logger.error("Failed to extract GithubException details", exc_info=e)

            error_message = _("An error occurred while saving. Please try again.")
            self.app.call_from_thread(self.show_error, error_message)

    def show_success(self, message: str) -> None:
        self.query_one("#loading-anim").display = False
        self.query_one("#loading-msg").display = False

        result_container = self.query_one("#loading-result-container")
        result_container.display = True

        icon = self.query_one("#result-icon", Static)
        icon.update("🎉")
        icon.add_class("success-icon")

        msg = self.query_one("#result-msg", Static)
        msg.update(message)

        pr_url_widget = self.query_one("#pr-url", Static)
        if self.pr_url:
            pr_url_widget.update(self.pr_url)
            self.query_one("#btn-open-pr").display = True
            self.query_one("#btn-copy-url").display = True
        else:
            pr_url_widget.display = False
            self.query_one("#btn-open-pr").display = False
            self.query_one("#btn-copy-url").display = False

        self.query_one("#btn-back").display = False
        self.query_one("#loading-actions").display = True

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

        self.query_one("#pr-url").display = False
        self.query_one("#btn-open-pr").display = False
        self.query_one("#btn-copy-url").display = False
        self.query_one("#btn-back").display = True

        self.query_one("#loading-actions").display = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-quit":

            def check_quit(quit_app: bool | None) -> None:
                if quit_app:
                    self.app.exit()

            self.app.push_screen(QuitConfirmScreen(), check_quit)
        elif event.button.id == "btn-open-pr":
            if self.pr_url:
                import webbrowser

                webbrowser.open(self.pr_url)
        elif event.button.id == "btn-copy-url":
            if self.pr_url:
                self.app.copy_to_clipboard(self.pr_url)
                self.notify(_("URL copied to clipboard!"))
