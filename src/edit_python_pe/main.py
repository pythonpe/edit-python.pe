import glob
import os

from github.Repository import Repository
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Event
from textual.types import NoSelection
from textual.widgets import (Button, Input, ListItem, ListView, Select, Static,
                             TextArea)

from .constants import (BITBUCKET_OPTION, FACEBOOK_OPTION, GITHUB_OPTION,
                        GITLAB_OPTION, INSTAGRAM_OPTION, LINKEDIN_OPTION,
                        X_OPTION, YOUTUBE_OPTION)
from .strings import (BUTTON_ADD, BUTTON_ADD_ALIAS, BUTTON_ADD_SOCIAL,
                      BUTTON_BACK, BUTTON_DELETE, BUTTON_QUIT, BUTTON_SAVE,
                      FORM_HEADER, LIST_TITLE, MESSAGE_EXIT, PLACEHOLDER_ALIAS,
                      PLACEHOLDER_CITY, PLACEHOLDER_EMAIL,
                      PLACEHOLDER_HOMEPAGE, PLACEHOLDER_NAME,
                      PLACEHOLDER_SOCIAL_URL, PROMPT_SOCIAL_NETWORK,
                      SECTION_ALIASES, SECTION_AVAIL, SECTION_CONTRIB,
                      SECTION_PYTHON, SECTION_SOCIAL, SECTION_WHO)
from .utils import (build_md_content, create_pr, fork_repo, get_repo,
                    load_file_into_form)


class SocialEntry(Horizontal):
    DEFAULT_CSS = """
        SocialEntry Select {
            width: 25%;
        }
        SocialEntry Input {
            width: 50%;
        }
        SocialEntry Button {
            width: 25%;
        }
    """

    def __init__(self, index: int, value: str) -> None:
        super().__init__()
        self.index = index
        self.select = Select(
            options=[
                GITHUB_OPTION,
                GITLAB_OPTION,
                BITBUCKET_OPTION,
                LINKEDIN_OPTION,
                FACEBOOK_OPTION,
                INSTAGRAM_OPTION,
                X_OPTION,
                YOUTUBE_OPTION,
            ],
            prompt=PROMPT_SOCIAL_NETWORK,
            value=value,
        )
        self.url_input = Input(placeholder=PLACEHOLDER_SOCIAL_URL)
        self.delete_btn = Button(BUTTON_DELETE, id=f"delete_social_{index}")

    def compose(self) -> ComposeResult:
        yield self.select
        yield self.url_input
        yield self.delete_btn


class AliasEntry(Horizontal):
    DEFAULT_CSS = """
        AliasEntry Input {
            width: 75%;
        }
        AliasEntry Button {
            width: 25%;
        }
    """

    def __init__(self, index: int) -> None:
        super().__init__()
        self.index = index
        self.alias_input = Input(placeholder=PLACEHOLDER_ALIAS)
        self.delete_btn = Button(BUTTON_DELETE, id=f"delete_alias_{index}")

    def compose(self) -> ComposeResult:
        yield self.alias_input
        yield self.delete_btn


class MemberApp(App):
    """Single app that toggles between a file list and a form while connected to a GitHub fork+push flow."""

    def __init__(
        self,
        original_repo: Repository,
        forked_repo: Repository,
        token: str,
        repo_path: str,
    ) -> None:
        super().__init__()
        self.original_repo = original_repo
        self.forked_repo = forked_repo
        self.token = token
        self.repo_path = repo_path

    def compose(self) -> ComposeResult:
        # Two main containers: self.list_container for the file list, self.form_container for the form.
        self.list_container = Vertical()
        yield self.list_container

        self.form_container = Vertical()
        yield self.form_container

    def on_mount(self) -> None:
        # 1) Build the list portion
        self.list_title = Static(LIST_TITLE)
        self.list_view = ListView()
        self.quit_list_button = Button(BUTTON_QUIT, id="quit_list")

        self.list_container.mount(self.list_title)
        self.add_list_button = Button(BUTTON_ADD, id="add_list")
        self.list_container.mount(self.list_view)
        self.list_container.mount(self.add_list_button)
        self.list_container.mount(self.quit_list_button)

        md_files = glob.glob(
            os.path.join(self.repo_path, "blog", "members", "*.md")
        )
        for f in md_files:
            basename = os.path.basename(f)
            self.list_view.append(ListItem(Static(basename)))

        # 2) Build the form portion, hidden at first
        self.form_header = Static(FORM_HEADER, classes="header")
        self.name_input = Input(placeholder=PLACEHOLDER_NAME)
        self.email_input = Input(placeholder=PLACEHOLDER_EMAIL)
        self.city_input = Input(placeholder=PLACEHOLDER_CITY)
        self.homepage_input = Input(placeholder=PLACEHOLDER_HOMEPAGE)

        self.who_area = TextArea()
        self.python_area = TextArea()
        self.contributions_area = TextArea()
        self.availability_area = TextArea()

        self.social_container = Vertical()
        self.alias_container = Vertical()
        self.add_social_button = Button(BUTTON_ADD_SOCIAL, id="add_social")
        self.add_alias_button = Button(BUTTON_ADD_ALIAS, id="add_alias")

        self.save_button = Button(BUTTON_SAVE, id="save")
        self.back_button = Button(BUTTON_BACK, id="back")
        self.quit_button = Button(BUTTON_QUIT, id="quit")

        # 3) Mount them in the form container
        self.form_container.mount(self.form_header)
        self.form_container.mount(self.name_input)
        self.form_container.mount(self.email_input)

        self.form_container.mount(Static(SECTION_SOCIAL, classes="subheader"))
        self.form_container.mount(self.social_container)
        self.form_container.mount(self.add_social_button)

        self.form_container.mount(Static(SECTION_ALIASES, classes="subheader"))
        self.form_container.mount(self.alias_container)
        self.form_container.mount(self.add_alias_button)

        self.form_container.mount(self.city_input)
        self.form_container.mount(self.homepage_input)
        self.form_container.mount(Static(SECTION_WHO, classes="subheader"))
        self.form_container.mount(self.who_area)
        self.form_container.mount(Static(SECTION_PYTHON, classes="subheader"))
        self.form_container.mount(self.python_area)
        self.form_container.mount(
            Static(
                SECTION_CONTRIB,
                classes="subheader",
            )
        )
        self.form_container.mount(self.contributions_area)
        self.form_container.mount(
            Static(
                SECTION_AVAIL,
                classes="subheader",
            )
        )
        self.form_container.mount(self.availability_area)

        self.form_button_bar = Horizontal(
            self.save_button, self.back_button, self.quit_button
        )
        self.form_container.mount(self.form_button_bar)

        self.form_container.display = False

        # Some data structures
        self.social_entries: list[SocialEntry] = []
        self.alias_entries: list[AliasEntry] = []
        self.social_index = 0
        self.alias_index = 0
        self.current_file = None

        # Show the list at startup
        self.show_list()

    def show_list(self) -> None:
        self.list_container.display = True
        self.form_container.display = False

    def show_form(self) -> None:
        self.list_container.display = False
        self.form_container.display = True

    def clear_form(self) -> None:
        """Clear out text fields / dynamic containers."""
        self.name_input.value = ""
        self.email_input.value = ""
        self.city_input.value = ""
        self.homepage_input.value = ""
        self.who_area.text = ""
        self.python_area.text = ""
        self.contributions_area.text = ""
        self.availability_area.text = ""

        for soc in self.social_entries:
            soc.remove()
        self.social_entries.clear()
        self.social_index = 0
        self.social_container.remove_children()

        for ali in self.alias_entries:
            ali.remove()
        self.alias_entries.clear()
        self.alias_index = 0
        self.alias_container.remove_children()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """User clicked on a file in the list. Parse it into the form fields."""
        item_text_widget = event.item.children[0]
        filename = item_text_widget.content
        self.current_file = filename

        self.clear_form()
        load_file_into_form(self, filename)
        self.show_form()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "quit_list":
            self.exit(message=MESSAGE_EXIT)
        elif bid == "add_social":
            self.add_social_entry()
        elif bid == "add_alias":
            self.add_alias_entry()
        elif bid == "add_list":
            self.clear_form()
            self.current_file = None
            self.show_form()
        elif bid == "save":
            self.save_member()
        elif bid == "back":
            # discard changes
            self.clear_form()
            self.show_list()
        elif bid == "quit":
            self.exit(message=MESSAGE_EXIT)
        elif bid and bid.startswith("delete_social_"):
            index = int(bid.replace("delete_social_", ""))
            self.remove_social_entry(index)
        elif bid and bid.startswith("delete_alias_"):
            index = int(bid.replace("delete_alias_", ""))
            self.remove_alias_entry(index)

    def add_social_entry(
        self, value: str | NoSelection = Select.BLANK
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

    def save_member(self) -> None:
        name = self.name_input.value.strip()
        email = self.email_input.value.strip()
        city = self.city_input.value.strip()
        homepage = self.homepage_input.value.strip()
        who = self.who_area.text.strip()
        python_ = self.python_area.text.strip()
        contributions = self.contributions_area.text.strip()
        availability = self.availability_area.text.strip()

        # aliases
        aliases = []
        for row in self.alias_entries:
            alias_val = row.alias_input.value.strip()
            if alias_val:
                aliases.append(alias_val)

        # socials
        socials = []
        for se in self.social_entries:
            plat = se.select.value
            urlval = se.url_input.value.strip()
            if plat and urlval:
                socials.append((plat, urlval))

        # Build the markdown doc as per the provided guide
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

        message = create_pr(
            md_content,
            self.current_file,
            self.repo_path,
            self.original_repo,
            self.forked_repo,
            self.token,
            aliases,
            name,
            email,
        )
        self.exit(message=message)

    async def on_event(self, event: Event) -> None:
        # catch listview selection
        if isinstance(event, ListView.Selected):
            self.on_list_view_selected(event)

        await super().on_event(event)


def main() -> None:
    token, original_repo = get_repo()
    repo_path, forked_repo = fork_repo(token, original_repo)
    app = MemberApp(original_repo, forked_repo, token, repo_path)
    app.run()


if __name__ == "__main__":
    main()
