import gettext
import locale
from pathlib import Path

from .constants import EN_LOCALE, ES_LOCALE, FR_LOCALE, IT_LOCALE

default_locale = locale.getlocale()[0] or EN_LOCALE
localedir = Path(__file__).parent.parent / "translations"
_ = gettext.translation(
    domain="messages",
    localedir=localedir,
    languages=[default_locale, ES_LOCALE, IT_LOCALE, FR_LOCALE],
    fallback=True,
).gettext

# Field, control, and message labels for edit_python_pe

# List and form titles
LIST_TITLE = _("Files in 'blog/members':")
FORM_HEADER = _("Member Form")

# Button labels
BUTTON_QUIT = _("Quit")
BUTTON_ADD = _("Add")
BUTTON_SAVE = _("Save")
BUTTON_BACK = _("Back")
BUTTON_ADD_SOCIAL = _("Add Social Network")
BUTTON_ADD_ALIAS = _("Add Alias")
BUTTON_DELETE = _("Delete")

# Input placeholders
PLACEHOLDER_NAME = _("Name")
PLACEHOLDER_EMAIL = _("Email")
PLACEHOLDER_CITY = _("City")
PLACEHOLDER_HOMEPAGE = _("Homepage")
PLACEHOLDER_SOCIAL_URL = _("Social network URL")
PLACEHOLDER_ALIAS = _("Alias")

# Control prompts
PROMPT_SOCIAL_NETWORK = _("Social Network")

# Section headers
SECTION_SOCIAL = _("Social Networks")
SECTION_ALIASES = _("Aliases")
SECTION_WHO = _("Who are you and what do you do?")
SECTION_PYTHON = _("How do you program in Python?")
SECTION_CONTRIB = _("Do you have any contributions to the Python community?")
SECTION_AVAIL = _("Are you available for mentoring, consulting, talks?")

# Messages
MESSAGE_PROMPT_FOR_GITHUB_TOKEN = _(
    "Please enter your GitHub personal access token: "
)
MESSAGE_EXIT = _("See you next time!")
MESSAGE_FILE_READ_ERROR = _("Error reading file {filename}: {error}")
MESSAGE_UNAUTHORIZED = _(
    "Unauthorized access. Please check your access token."
)
MESSAGE_REPO_NOT_FOUND = _(
    "Repository not found. Please check your access token."
)
MESSAGE_FILE_EDITED_PR = _(
    "File {name_file} edited, commit and changes sent to existing PR."
)
MESSAGE_FILE_SAVED_PR = _("File {name_file} saved, commit and PR ready.")
MESSAGE_CREATE_ENTRY = _(
    "Creating a new entry to `blog/members` for {name} (alias: {first_alias})."
)
MESSAGE_CHANGE_ENTRY = _(
    "Changing an entry to `blog/members` for {name} (alias: {first_alias})."
)
MESSAGE_LOAD_FILE_ERROR = _("Error reading file {filename}: {error}")

# build_md_content markdown dictionary (English keys, Spanish values for now)
MD_CONTENT = {
    "yaml_start": "---",
    "yaml_blogpost": "blogpost: true",
    "yaml_date": "date: {date}",
    "yaml_author": "author: {author}",
    "yaml_location": "location: {city}",
    "yaml_category": "category: members",
    "yaml_language": "language: Español",
    "yaml_image": "image: 1",
    "yaml_excerpt": "excerpt: 1",
    "yaml_end": "---",
    "header_name": "# {name}",
    "gravatar_block": '```{{gravatar}} {email}\n---\nwidth: 200\nclass: "member-gravatar"\n---\n```',
    "social_block_start": "```{{raw}} html",
    "social_ul_start": '<ul class="social-media profile">',
    "social_li": '    <li>\n        <a class="external reference" href="{url}">\n            <iconify-icon icon="simple-icons:{platform}" style="font-size:2em"></iconify-icon>\n        </a>\n    </li>',
    "social_ul_end": "</ul>",
    "social_block_end": "```",
    "aliases": ":Aliases: {aliases}",
    "city": ":Ciudad: {city}",
    "homepage": ":Homepage: {homepage}",
    "section_about": "## Sobre mí",
    "section_who": "### ¿Quién eres y a qué te dedicas?",
    "section_python": "### ¿Cómo programas en Python?",
    "section_contrib": "### ¿Tienes algún aporte a la comunidad de Python?",
    "section_avail": "### ¿Estás disponible para hacer mentoring, consultorías, charlas?",
}
