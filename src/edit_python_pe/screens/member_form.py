import re
from typing import TYPE_CHECKING, cast

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.types import NoSelection
from textual.widgets import Button, Input, Select, Static, TextArea

if TYPE_CHECKING:
    from ..app import MemberApp

from ..components.alias_entry import AliasEntry
from ..components.form_control import FormControl
from ..components.layout import AppFooter, AppHeader
from ..components.social_entry import SocialEntry
from ..markdown_builder import build_md_content, load_file_into_form
from ..strings import _
from .quit_confirm import QuitConfirmScreen
from .save_loading import SaveLoadingScreen

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
URL_REGEX = re.compile(
    r"^(https?://)?[\w.-]+(?:\.[\w.-]+)+[\w\-._~:/?#[\]@!$&'()*+,;=.]*$"
)


class DiscardConfirmScreen(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        with Vertical(id="member-form-discard-dialog"):
            yield Static(
                _("Are you sure you want to discard your changes?"),
                id="member-form-discard-dialog-msg",
            )
            with Horizontal(id="member-form-discard-dialog-actions"):
                yield Button(
                    _("Cancel"),
                    id="member-form-discard-cancel",
                    variant="primary",
                )
                yield Button(
                    _("Discard"),
                    id="member-form-discard-confirm",
                    variant="error",
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "member-form-discard-cancel":
            self.dismiss(False)
        elif event.button.id == "member-form-discard-confirm":
            self.dismiss(True)


class MemberFormScreen(Screen):
    BINDINGS = [
        ("escape", "back", "Go Back / Discard"),
        ("ctrl+s", "save", "Save Member"),
    ]

    def __init__(self, filename: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.current_file = filename
        self.social_entries: list[SocialEntry] = []
        self.alias_entries: list[AliasEntry] = []
        self.social_index = 0
        self.alias_index = 0

    def compose(self) -> ComposeResult:
        yield AppHeader()
        with VerticalScroll(id="member-form-scroll-container"):
            # Required fields
            yield FormControl(
                Input(placeholder=_("Name"), id="member-form-name"),
                label=_("Name:") + " [red]*[/red]",
                id="control-name",
            )
            yield FormControl(
                Input(placeholder=_("Email"), id="member-form-email"),
                label=_("Email:") + " [red]*[/red]",
                id="control-email",
            )

            # Dynamic lists
            yield Static(_("Social Networks"), classes="subheader")
            yield Vertical(id="member-form-social-container")
            yield Button(
                _("Add Social Network"),
                id="member-form-add-social",
                variant="primary",
            )

            # Alias list
            yield Static(_("Aliases"), classes="subheader")
            yield Vertical(id="member-form-alias-container")
            yield Button(_("Add Alias"), id="member-form-add-alias", variant="primary")

            yield FormControl(
                Input(placeholder=_("City"), id="member-form-city"),
                label=_("City:"),
                id="control-city",
            )
            yield FormControl(
                Input(placeholder=_("Homepage"), id="member-form-homepage"),
                label=_("Homepage:"),
                id="control-homepage",
            )

            yield FormControl(
                TextArea(id="member-form-who"),
                label=_("Who are you and what do you do?"),
                id="control-who",
            )
            yield FormControl(
                TextArea(id="member-form-python"),
                label=_("How do you program in Python?"),
                id="control-python",
            )
            yield FormControl(
                TextArea(id="member-form-contributions"),
                label=_("Do you have any contributions to the Python community?"),
                id="control-contributions",
            )
            yield FormControl(
                TextArea(id="member-form-availability"),
                label=_("Are you available for mentoring, consulting, talks?"),
                id="control-availability",
            )

        with Horizontal(id="member-form-actions"):
            with Horizontal(id="member-form-actions-left"):
                yield Button(_("Save"), id="member-form-save", variant="primary")
            with Horizontal(id="member-form-actions-right"):
                yield Button(_("Discard"), id="member-form-discard", variant="warning")
                yield Button(_("Quit"), id="member-form-quit", variant="error")
        yield AppFooter()

    def on_mount(self) -> None:
        self.name_input = self.query_one("#member-form-name", Input)
        self.name_control = self.query_one("#control-name", FormControl)

        self.email_input = self.query_one("#member-form-email", Input)
        self.email_control = self.query_one("#control-email", FormControl)

        self.city_input = self.query_one("#member-form-city", Input)

        self.homepage_input = self.query_one("#member-form-homepage", Input)
        self.homepage_control = self.query_one("#control-homepage", FormControl)

        self.who_area = self.query_one("#member-form-who", TextArea)
        self.python_area = self.query_one("#member-form-python", TextArea)
        self.contributions_area = self.query_one("#member-form-contributions", TextArea)
        self.availability_area = self.query_one("#member-form-availability", TextArea)
        self.social_container = self.query_one(
            "#member-form-social-container", Vertical
        )
        self.alias_container = self.query_one("#member-form-alias-container", Vertical)

        if self.current_file:
            load_file_into_form(self, self.current_file)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "member-form-add-social":
            self.add_social_entry()
        elif bid == "member-form-add-alias":
            self.add_alias_entry()
        elif bid == "member-form-save":
            self.action_save()
        elif bid == "member-form-discard":
            self.action_back()
        elif event.button.id == "member-form-quit":

            def check_quit(quit_app: bool | None) -> None:
                if quit_app:
                    self.app.exit()

            self.app.push_screen(QuitConfirmScreen(), check_quit)
        elif bid and bid.startswith("delete_social_"):
            index = int(bid.replace("delete_social_", ""))
            self.remove_social_entry(index)
        elif bid and bid.startswith("delete_alias_"):
            index = int(bid.replace("delete_alias_", ""))
            self.remove_alias_entry(index)

    def add_social_entry(
        self,
        value: str | NoSelection = Select.NULL,
    ) -> None:
        new_entry = SocialEntry(self.social_index, value)
        self.social_index += 1
        self.social_entries.append(new_entry)
        self.social_container.mount(new_entry)

    def remove_social_entry(self, index: int) -> None:
        found = None
        for e in self.social_entries:
            if e.index == index:
                found = e
                break
        if found:
            self.social_entries.remove(found)
            found.remove()

    def add_alias_entry(self) -> None:
        row = AliasEntry(self.alias_index)
        self.alias_index += 1
        self.alias_entries.append(row)
        self.alias_container.mount(row)

    def remove_alias_entry(self, index: int) -> None:
        found = None
        for a in self.alias_entries:
            if a.index == index:
                found = a
                break
        if found:
            self.alias_entries.remove(found)
            found.remove()

    def _validate_basic_fields(self) -> bool:
        has_errors = False
        name = self.name_input.value.strip()
        email = self.email_input.value.strip()
        if not name:
            self.name_control.show_error(_("Name is required."))
            has_errors = True
        if not email:
            self.email_control.show_error(_("Email is required."))
            has_errors = True
        elif not EMAIL_REGEX.match(email):
            self.email_control.show_error(_("Invalid email format."))
            has_errors = True

        homepage = self.homepage_input.value.strip()
        if homepage and not URL_REGEX.match(homepage):
            self.homepage_control.show_error(_("Invalid homepage URL format."))
            has_errors = True
        return has_errors

    def _validate_social_entries(self) -> bool:
        has_errors = False
        for se in self.social_entries:
            plat = se.select.value
            urlval = se.url_input.value.strip()
            if bool(plat) != bool(urlval):
                se.show_error(
                    _("Both platform and URL must be provided if either is set.")
                )
                has_errors = True
            elif urlval and not URL_REGEX.match(urlval):
                se.show_error(_("Invalid URL format for social network."))
                has_errors = True
        return has_errors

    def save_member(self) -> None:
        self.name_control.clear_error()
        self.email_control.clear_error()
        self.homepage_control.clear_error()
        for se in self.social_entries:
            se.clear_error()

        basic_errors = self._validate_basic_fields()
        social_errors = self._validate_social_entries()

        if basic_errors or social_errors:
            return

        name = self.name_input.value.strip()
        email = self.email_input.value.strip()
        city = self.city_input.value.strip()
        homepage = self.homepage_input.value.strip()
        who = self.who_area.text.strip()
        python_ = self.python_area.text.strip()
        contributions = self.contributions_area.text.strip()
        availability = self.availability_area.text.strip()

        aliases = []
        for row in self.alias_entries:
            alias_val = row.alias_input.value.strip()
            if alias_val:
                aliases.append(alias_val)

        socials = []
        for se in self.social_entries:
            plat = se.select.value
            urlval = se.url_input.value.strip()
            if plat and urlval:
                socials.append((str(plat), urlval))

        md_content = build_md_content(
            name,
            email,
            aliases,
            socials,
            city,
            homepage,
            who,
            python_,
            contributions,
            availability,
        )

        app = cast("MemberApp", self.app)

        if (
            app.original_repo is None
            or app.forked_repo is None
            or app.repo_path is None
            or app.token is None
        ):
            self.app.notify(
                _("GitHub repositories are not initialized."), severity="error"
            )
            return

        self.app.push_screen(
            SaveLoadingScreen(
                file_content=md_content,
                current_file=self.current_file,
                repo_path=app.repo_path,
                original_repo=app.original_repo,
                forked_repo=app.forked_repo,
                token=app.token,
                aliases=aliases,
                name=name,
                email=email,
            )
        )

    def action_back(self) -> None:
        def check_discard(discard: bool | None) -> None:
            if discard:
                self.app.pop_screen()
                if self.current_file:
                    self.app.pop_screen()

        self.app.push_screen(DiscardConfirmScreen(), check_discard)

    def action_save(self) -> None:
        self.save_member()
