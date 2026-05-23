import gettext
from pathlib import Path

from .constants import EN_LOCALE

localedir = Path(__file__).parent / "locale"
_translator = gettext.translation(
    domain="messages",
    localedir=localedir,
    languages=[EN_LOCALE],
    fallback=True,
)


def set_language(lang_code: str) -> None:
    """Dynamically switch the active translation domain."""
    global _translator
    _translator = gettext.translation(
        domain="messages",
        localedir=localedir,
        languages=[lang_code],
        fallback=True,
    )


def _(message: str) -> str:
    """Translate a message using the currently active language."""
    return _translator.gettext(message)


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
    "gravatar_block": '```{{gravatar}} {email}\n---\nwidth: 200\nclass: "member-gravatar"\n---\n```',  # noqa: E501
    "social_block_start": "```{{raw}} html",
    "social_ul_start": '<ul class="social-media profile">',
    "social_li": '    <li>\n        <a class="external reference" href="{url}">\n            <iconify-icon icon="simple-icons:{platform}" style="font-size:2em"></iconify-icon>\n        </a>\n    </li>',  # noqa: E501
    "social_ul_end": "</ul>",
    "social_block_end": "```",
    "aliases": ":Aliases: {aliases}",
    "city": ":Ciudad: {city}",
    "homepage": ":Homepage: {homepage}",
    "section_about": "## Sobre mí",
    "section_who": "### ¿Quién eres y a qué te dedicas?",
    "section_python": "### ¿Cómo programas en Python?",
    "section_contrib": "### ¿Tienes algún aporte a la comunidad de Python?",
    "section_avail": "### ¿Estás disponible para hacer mentoring, consultorías, charlas?",  # noqa: E501
}
