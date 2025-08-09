import os
import re
import glob
import getpass
import hashlib
from datetime import datetime

import pygit2
from github import Github
from github.Repository import Repository
from github.GithubException import BadCredentialsException, GithubException

from textual.app import App, ComposeResult
from textual.events import Event
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Static,
    Button,
    Input,
    TextArea,
    Select,
    ListView,
    ListItem,
)


class MemberApp(App):
    """Single app that toggles between a file list and a form while connected to a GitHub fork+push flow."""

    def __init__(self, token: str, original_repo: Repository) -> None:
        super().__init__()
        self.token = token
        self.original_repo = original_repo

    def compose(self) -> ComposeResult:
        # Two main containers: self.list_container for the file list, self.form_container for the form.
        self.list_container = Vertical()
        yield self.list_container

        self.form_container = Vertical()
        yield self.form_container

    def on_mount(self) -> None:
        """Perform setup: ask for token, do fork if needed, set up UI."""
        self.forked_repo = self.original_repo.create_fork()
        self.FORKED_REPO_URL = self.forked_repo.clone_url
        self.REPO_PATH = "python.pe"

        if not os.path.exists(self.REPO_PATH):
            callbacks = pygit2.callbacks.RemoteCallbacks(
                credentials=pygit2.UserPass(self.token, "x-oauth-basic")
            )
            pygit2.clone_repository(
                self.FORKED_REPO_URL, self.REPO_PATH, callbacks=callbacks
            )

        # 2) Build the list portion
        self.list_title = Static("Archivos en 'blog/members':")
        self.list_view = ListView()
        self.quit_list_button = Button("Salir", id="quit_list")

        self.list_container.mount(self.list_title)
        self.list_container.mount(self.list_view)
        self.list_container.mount(self.quit_list_button)

        md_files = glob.glob(os.path.join(self.REPO_PATH, "blog", "members", "*.md"))
        for f in md_files:
            basename = os.path.basename(f)
            self.list_view.append(ListItem(Static(basename)))

        # 3) Build the form portion, hidden at first
        self.form_header = Static("Formulario de Miembro", classes="header")
        self.name_input = Input(placeholder="Nombre")
        self.email_input = Input(placeholder="Correo electrónico")
        self.city_input = Input(placeholder="Ciudad")
        self.homepage_input = Input(placeholder="Página personal")

        self.about_me_area = TextArea(text="Sobre mí")
        self.who_area = TextArea(text="¿Quién eres y a qué te dedicas?")
        self.python_area = TextArea(text="¿Cómo programas en Python?")
        self.contributions_area = TextArea(
            text="¿Tienes algún aporte a la comunidad de Python?"
        )
        self.availability_area = TextArea(
            text="¿Estás disponible para hacer mentoring, consultorías, charlas?"
        )

        self.social_container = Vertical()
        self.alias_container = Vertical()
        self.add_social_button = Button("Agregar Red Social", id="add_social")
        self.add_alias_button = Button("Agregar Alias", id="add_alias")

        self.save_button = Button("Guardar", id="save")
        self.back_button = Button("Atrás", id="back")
        self.quit_button = Button("Salir", id="quit")

        # Mount them in the form container
        self.form_container.mount(self.form_header)
        self.form_container.mount(self.name_input)
        self.form_container.mount(self.email_input)

        self.form_container.mount(Static("Redes Sociales", classes="subheader"))
        self.form_container.mount(self.social_container)
        self.form_container.mount(self.add_social_button)

        self.form_container.mount(Static("Aliases", classes="subheader"))
        self.form_container.mount(self.alias_container)
        self.form_container.mount(self.add_alias_button)

        self.form_container.mount(self.city_input)
        self.form_container.mount(self.homepage_input)
        self.form_container.mount(self.about_me_area)
        self.form_container.mount(self.who_area)
        self.form_container.mount(self.python_area)
        self.form_container.mount(self.contributions_area)
        self.form_container.mount(self.availability_area)

        self.form_button_bar = Horizontal(
            self.save_button, self.back_button, self.quit_button
        )
        self.form_container.mount(self.form_button_bar)

        self.form_container.display = False

        # Some data structures
        self.social_entries = []
        self.alias_entries = []
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
        self.about_me_area.text = ""
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
        filename = item_text_widget.renderable
        self.current_file = filename

        self.clear_form()
        self.load_file_into_form(filename)
        self.show_form()

    def load_file_into_form(self, filename: str) -> None:
        path_md = os.path.join(self.REPO_PATH, "blog", "members", filename)
        if not os.path.exists(path_md):
            return
        try:
            with open(path_md, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception as e:
                self.exit(f"Error loading file {filename}: {e}")
                return
    
        self.clear_form()

        # Extract YAML frontmatter
        yaml_match = re.search(r"---\n(.*?)---\n", content, re.DOTALL)
        yaml_data = {}
        if yaml_match:
            try:
                import yaml
                yaml_data = yaml.safe_load(yaml_match.group(1))
            except Exception:
                yaml_data = {}
        self.name_input.value = yaml_data.get("author", "")
        self.city_input.value = yaml_data.get("location", "")

        # Extract member name from first markdown header
        name_match = re.search(r"^# (.+)", content, re.MULTILINE)
        if name_match:
            self.name_input.value = name_match.group(1).strip()

        # Extract gravatar email
        gravatar_match = re.search(r"```\{gravatar\} ([^\n]+)", content)
        if gravatar_match:
            self.email_input.value = gravatar_match.group(1).strip()

        # Extract social links from raw HTML block
        social_block = re.search(r"```\{raw\} html\n(.*?)```", content, re.DOTALL)
        if social_block:
            social_html = social_block.group(1)
            social_link_pattern = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>\s*<iconify-icon[^>]*icon="simple-icons:([^"]+)"', re.DOTALL)
            for match in social_link_pattern.finditer(social_html):
                url = match.group(1)
                platform = match.group(2)
                self.add_social_entry()
                last_entry = self.social_entries[-1]
                last_entry.select.value = platform
                last_entry.url_input.value = url

        # Extract aliases, city, homepage from colon-prefixed lines
        alias_match = re.search(r":Aliases:\s*([^\n]+)", content)
        if alias_match:
            aliases = [a.strip() for a in alias_match.group(1).split(",")]
            for alias_val in aliases:
                self.add_alias_entry()
                self.alias_entries[-1].alias_input.value = alias_val
        city_match = re.search(r":Ciudad:\s*([^\n]+)", content)
        if city_match:
            self.city_input.value = city_match.group(1).strip()
        homepage_match = re.search(r":Homepage:\s*([^\n]+)", content)
        if homepage_match:
            self.homepage_input.value = homepage_match.group(1).strip()

        # Extract markdown sections under headers
        sobre_mi_match = re.search(r"## Sobre mí\n(.*?)(?=^### |\Z)", content, re.DOTALL | re.MULTILINE)
        if sobre_mi_match:
            self.about_me_area.text = sobre_mi_match.group(1).strip()
        who_match = re.search(r"### ¿Quién eres y a qué te dedicas\?\n(.*?)(?=^### |\Z)", content, re.DOTALL | re.MULTILINE)
        if who_match:
            self.who_area.text = who_match.group(1).strip()
        python_match = re.search(r"### ¿Cómo programas en Python\?\n(.*?)(?=^### |\Z)", content, re.DOTALL | re.MULTILINE)
        if python_match:
            self.python_area.text = python_match.group(1).strip()
        contrib_match = re.search(r"### ¿Tienes algún aporte a la comunidad de Python\?\n(.*?)(?=^### |\Z)", content, re.DOTALL | re.MULTILINE)
        if contrib_match:
            self.contributions_area.text = contrib_match.group(1).strip()
        avail_match = re.search(r"### ¿Estás disponible para hacer mentoring, consultorías, charlas\?\n(.*?)(?=^### |\Z)", content, re.DOTALL | re.MULTILINE)
        if avail_match:
            self.availability_area.text = avail_match.group(1).strip()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "quit_list":
            self.exit("¡Hasta la próxima!")
        elif bid == "add_social":
            self.add_social_entry()
        elif bid == "add_alias":
            self.add_alias_entry()
        elif bid == "save":
            self.save_member()
        elif bid == "back":
            # discard changes
            self.clear_form()
            self.show_list()
        elif bid == "quit":
            self.exit("Saliendo de la aplicación.")
        elif bid and bid.startswith("delete_social_"):
            index = int(bid.replace("delete_social_", ""))
            self.remove_social_entry(index)
        elif bid and bid.startswith("delete_alias_"):
            index = int(bid.replace("delete_alias_", ""))
            self.remove_alias_entry(index)

    def add_social_entry(self) -> None:
        class SocialEntry(Horizontal):
            def __init__(se, index):
                super().__init__()
                se.index = index
                se.select = Select(
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
                se.url_input = Input(placeholder="URL de la red social")
                se.delete_btn = Button("Eliminar", id=f"delete_social_{index}")

            def compose(se) -> ComposeResult:
                yield se.select
                yield se.url_input
                yield se.delete_btn

        new_entry = SocialEntry(self.social_index)
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
        class AliasEntryRow(Horizontal):
            def __init__(se, index):
                super().__init__()
                se.index = index
                se.alias_input = Input(placeholder="Alias")
                se.delete_btn = Button("Eliminar", id=f"delete_alias_{index}")

            def compose(se) -> ComposeResult:
                yield se.alias_input
                yield se.delete_btn

        row = AliasEntryRow(self.alias_index)
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
        about_me = self.about_me_area.text.strip()
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

        # compute name_file
        if aliases:
            alias_for_name = aliases[0].lower().replace(" ", "_")
        else:
            alias_for_name = name.lower().replace(" ", "_")

        sha_hash = hashlib.sha1(
            (alias_for_name + email + datetime.now().isoformat()).encode("utf-8")
        ).hexdigest()[:8]
        name_file = f"{alias_for_name}-{sha_hash}"

        # Build the markdown doc as per the provided guide
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
            "% NOTA: No olvidar poner la fecha de publicación debajo de `blogpost: true`",
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
        if socials:
            md_lines.append("```{raw} html")
            md_lines.append('<ul class="social-media profile">')
            for plat, url in socials:
                md_lines.append("    <li>")
                md_lines.append(f'        <a class="external reference" href="{url}">')
                md_lines.append(f'            <iconify-icon icon="simple-icons:{plat}" style="font-size:2em"></iconify-icon>')
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

        if python_:
            md_lines.append("### ¿Cómo programas en Python?")
            md_lines.append("")
            md_lines.append(python_)
            md_lines.append("")

        if contributions:
            md_lines.append("### ¿Tienes algún aporte a la comunidad de Python?")
            md_lines.append("")
            md_lines.append(contributions)
            md_lines.append("")

        if availability:
            md_lines.append("### ¿Estás disponible para hacer mentoring, consultorías, charlas?")
            md_lines.append("")
            md_lines.append(availability)
            md_lines.append("")

        md_content = "\n".join(md_lines)

        # Write file
        file_path = os.path.join(self.REPO_PATH, "blog", "members", f"{name_file}.md")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # commit & push
        repo = pygit2.Repository(self.REPO_PATH)
        rel_path = os.path.relpath(file_path, self.REPO_PATH)
        repo.index.add(rel_path)
        repo.index.write()
        author_sig = pygit2.Signature(name or "Unknown", email or "unknown@email")
        tree_id = repo.index.write_tree()
        parents = [] if repo.head_is_unborn else [repo.head.target]
        commit_msg = f"Added {name_file}.md"
        repo.create_commit("HEAD", author_sig, author_sig, commit_msg, tree_id, parents)

        callbacks = pygit2.callbacks.RemoteCallbacks(
            credentials=pygit2.UserPass(self.token, "x-oauth-basic")
        )
        remote = repo.remotes["origin"]
        remote.push([repo.head.name], callbacks=callbacks)

        # create PR
        pr_title = commit_msg
        first_alias = aliases[0] if aliases else ""
        pr_body = f"Creating a new entry to `blog/membbers` for {name} (alias: {first_alias})."
        fork_owner = self.forked_repo.owner.login
        head_branch = f"{fork_owner}:main"
        base_branch = "main"
        self.original_repo.create_pull(
            title=pr_title, body=pr_body, head=head_branch, base=base_branch
        )

        self.exit(f"Archivo {name_file}.md guardado, commit y PR listo.")

    async def on_event(self, event: Event) -> None:
        # catch listview selection
        if isinstance(event, ListView.Selected):
            self.on_list_view_selected(event)

        await super().on_event(event)


def get_repo() -> tuple[str, Repository]:
    token: str = getpass.getpass(
        "Por favor ingrese su access token personal de GitHub: "
    )
    g = Github(token)

    try:
        return token, g.get_repo("pythonpe/python.pe")
    except BadCredentialsException:
        print("Acceso no autorizado. Por favor, verifique su token de acceso.")
        exit(1)
    except GithubException:
        print("Repositorio no encontrado. Por favor, verifique su token de acceso.")
        exit(1)


def main() -> None:
    token, original_repo = get_repo()
    app = MemberApp(token=token, original_repo=original_repo)
    app.run()


if __name__ == "__main__":
    main()
