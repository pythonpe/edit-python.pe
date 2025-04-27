import os
from datetime import datetime
import getpass

import pygit2
from textual.app import App, ComposeResult
from textual.widgets import (
    Input,
    TextArea,
    Button,
    Static,
    Select,
    ListView as VerticalScroll,
)
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from github import Github
from github.GithubException import BadCredentialsException

# Ask for GitHub token
token = getpass.getpass("Por favor ingrese su access token personal de GitHub: ")
g = Github(token)

try:
    original_repo = g.get_repo("pythonpe/python.pe")
except BadCredentialsException:
    print("Acceso no autorizado. Por favor, verifique su token de acceso.")
    exit(1)
# Fork the repository, naming it python.pe
forked_repo = original_repo.create_fork()
FORKED_REPO_URL = forked_repo.clone_url

REPO_PATH = "python.pe"  # local folder name for the fork

if not os.path.exists(REPO_PATH):
    callbacks = pygit2.callbacks.RemoteCallbacks(
        credentials=pygit2.UserPass(token, "x-oauth-basic")
    )
    pygit2.clone_repository(FORKED_REPO_URL, REPO_PATH, callbacks=callbacks)


class SocialNetworkEntry(Horizontal):
    def __init__(self, index: int):
        super().__init__()
        self.index = index
        self.select = Select(
            options=[
                ("GitHub", "github"),
                ("GitLab", "gitlab"),
                ("Bitbucket", "bitbucket"),
                ("LinkedIn", "linkedin"),
                ("Facebook", "facebook"),
                ("Instagram", "instagram"),
                ("X", "x"),
                ("YouTube", "youtube"),
            ],
            prompt="Red Social",
        )
        self.url_input = Input(placeholder="URL de la red social", id="social_url")
        self.url_input.styles.width = 40
        self.select.styles.border = ("solid", "blue")  # For quick debugging
        self.select.styles.width = 30
        self.delete_button = Button("Eliminar", id=f"delete_social_{index}")
        self.delete_button.styles.width = 30

    def compose(self) -> ComposeResult:
        yield self.select
        yield self.url_input
        yield self.delete_button


class AliasEntry(Horizontal):
    def __init__(self, index: int):
        super().__init__()
        self.index = index
        self.alias_input = Input(placeholder="Alias")
        self.alias_input.styles.width = 40
        self.delete_button = Button("Eliminar", id=f"delete_alias_{index}")
        self.delete_button.styles.width = 30

    def compose(self) -> ComposeResult:
        yield self.alias_input
        yield self.delete_button


class MemberFormApp(App):
    CSS_PATH = None  # Disable CSS

    def __init__(self):
        super().__init__()
        self.social_entries = []
        self.alias_entries = []
        self.social_index = 0
        self.alias_index = 0

    def compose(self) -> ComposeResult:
        yield Static("Formulario de Miembro", classes="header")

        # Main fields
        self.name_file_input = Input(placeholder="Nombre del archivo (sin extensión)")
        self.name_input = Input(placeholder="Nombre")
        self.email_input = Input(placeholder="Correo electrónico")
        self.city_input = Input(placeholder="Ciudad")
        self.homepage_input = Input(placeholder="Página personal")

        yield self.name_file_input
        yield self.name_input
        yield self.email_input

        # Social media
        yield Static("Redes Sociales", classes="subheader")
        self.social_container = VerticalScroll()
        yield self.social_container
        self.add_social_button = Button("Agregar Red Social", id="add_social")
        yield self.add_social_button

        # Aliases
        yield Static("Aliases", classes="subheader")
        self.alias_container = VerticalScroll()
        yield self.alias_container
        self.add_alias_button = Button("Agregar Alias", id="add_alias")
        yield self.add_alias_button

        yield self.city_input
        yield self.homepage_input

        # Text areas
        self.about_me_area = TextArea(text="Sobre mí")
        self.who_area = TextArea(text="¿Quién eres y a qué te dedicas?")
        self.python_area = TextArea(text="¿Cómo programas en Python?")
        self.contributions_area = TextArea(
            text="¿Tienes algún aporte a la comunidad de Python?"
        )
        self.availability_area = TextArea(
            text="¿Estás disponible para hacer mentoring, consultorías, charlas?"
        )

        yield self.about_me_area
        yield self.who_area
        yield self.python_area
        yield self.contributions_area
        yield self.availability_area

        # Save button
        self.save_button = Button("Guardar", id="save")
        self.quit_button = Button("Salir", id="quit")
        yield Horizontal(self.save_button, self.quit_button)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "add_social":
            self.add_social_entry()
        elif button_id == "add_alias":
            self.add_alias_entry()
        elif button_id == "save":
            self.save_member()
        elif button_id and button_id.startswith("delete_social_"):
            index = int(button_id.replace("delete_social_", ""))
            self.remove_social_entry(index)
        elif button_id and button_id.startswith("delete_alias_"):
            index = int(button_id.replace("delete_alias_", ""))
            self.remove_alias_entry(index)
        elif button_id == "quit":
            self.exit()

    def add_social_entry(self):
        entry = SocialNetworkEntry(self.social_index)
        self.social_entries.append(entry)
        self.social_container.mount(entry)
        self.social_index += 1

    def remove_social_entry(self, index: int):
        entry = next((e for e in self.social_entries if e.index == index), None)
        if entry:
            self.social_entries.remove(entry)
            entry.remove()

    def add_alias_entry(self):
        entry = AliasEntry(self.alias_index)
        self.alias_entries.append(entry)
        self.alias_container.mount(entry)
        self.alias_index += 1

    def remove_alias_entry(self, index: int):
        entry = next((e for e in self.alias_entries if e.index == index), None)
        if entry:
            self.alias_entries.remove(entry)
            entry.remove()

    def save_member(self):
        name_file = self.name_file_input.value.strip()
        name = self.name_input.value.strip()
        email = self.email_input.value.strip()
        city = self.city_input.value.strip()
        homepage = self.homepage_input.value.strip()
        about_me = self.about_me_area.text.strip()
        who = self.who_area.text.strip()
        python = self.python_area.text.strip()
        contributions = self.contributions_area.text.strip()
        availability = self.availability_area.text.strip()

        social_links = []
        for entry in self.social_entries:
            platform = entry.select.value
            url = entry.url_input.value.strip()
            if platform and url:
                social_links.append((platform, url))

        aliases = [
            entry.alias_input.value.strip()
            for entry in self.alias_entries
            if entry.alias_input.value.strip()
        ]

        # Build the content of the Markdown file
        date_str = datetime.now().strftime("%Y-%m-%d")
        md_lines = [
            "---",
            "blogpost: true",
            f"author: {name}",
            f"location: {city}",
            "category: members",
            "language: Español",
            "image: 1",
            "excerpt: 1",
            "---",
            "",
            f"# {name}",
            "",
            f"```{{gravatar}} {email}",
            "---",
            "width: 200",
            'class: "member-gravatar"',
            "---",
            "```",
            "",
        ]

        if social_links:
            md_lines.append("```{raw} html")
            md_lines.append('<ul class="social-media profile">')
            for platform, url in social_links:
                md_lines.append("    <li>")
                md_lines.append(f'        <a class="external reference" href="{url}">')
                md_lines.append(
                    f'            <iconify-icon icon="simple-icons:{platform}" style="font-size:2em"></iconify-icon>'
                )
                md_lines.append("        </a>")
                md_lines.append("    </li>")
            md_lines.append("</ul>")
            md_lines.append("```")
            md_lines.append("")

        if aliases:
            md_lines.append(f":Aliases: {', '.join(aliases)}")
            md_lines.append("")

        if city:
            md_lines.append(f":Ciudad: {city}")
            md_lines.append("")

        if homepage:
            md_lines.append(f":Homepage: {homepage}")
            md_lines.append("")

        if about_me:
            md_lines.append("## Sobre mí")
            md_lines.append("")
            md_lines.append(about_me)
            md_lines.append("")

        if who:
            md_lines.append("### ¿Quién eres y a qué te dedicas?")
            md_lines.append("")
            md_lines.append(who)
            md_lines.append("")

        if python:
            md_lines.append("### ¿Cómo programas en Python?")
            md_lines.append("")
            md_lines.append(python)
            md_lines.append("")

        if contributions:
            md_lines.append("### ¿Tienes algún aporte a la comunidad de Python?")
            md_lines.append("")
            md_lines.append(contributions)
            md_lines.append("")

        if availability:
            md_lines.append(
                "### ¿Estás disponible para hacer mentoring, consultorías, charlas?"
            )
            md_lines.append("")
            md_lines.append(availability)
            md_lines.append("")

        md_content = "\n".join(md_lines)

        # Guardar el archivo
        file_path = os.path.join(REPO_PATH, "blog", "members", f"{name_file}.md")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Add and commit using pygit2
        repo = pygit2.Repository(REPO_PATH)
        repo.index.add(os.path.relpath(file_path, REPO_PATH))
        repo.index.write()
        author = pygit2.Signature(name, email)
        committer = pygit2.Signature(name, email)
        tree = repo.index.write_tree()
        if repo.head_is_unborn:
            parents = []
        else:
            parents = [repo.head.target]
        repo.create_commit(
            "HEAD", author, committer, f"Added {name_file}.md", tree, parents
        )

        # push to the remote
        callbacks = pygit2.callbacks.RemoteCallbacks(
            credentials=pygit2.UserPass(token, "x-oauth-basic")
        )
        remote = repo.remotes["origin"]
        remote.push([repo.head.name], callbacks=callbacks)

        # Create a Pull Request from the fork to the original repo
        pr_title = f"Added {name_file}.md"
        first_alias = aliases[0] if aliases else ""
        pr_body = f"Creating a new entry to `blog/membbers` for {name} (alias: {first_alias})."

        fork_owner = forked_repo.owner.login
        head_branch = f"{fork_owner}:main"
        base_branch = "main"

        original_repo.create_pull(
            title=pr_title, body=pr_body, head=head_branch, base=base_branch
        )

        self.exit(f"Archivo {name_file}.md guardado, commit realizado y PR creado.")


if __name__ == "__main__":
    app = MemberFormApp()
    app.run()
