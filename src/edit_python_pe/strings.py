# Field, control, and message labels for edit_python_pe

# List and form titles
LIST_TITLE = "Files in 'blog/members':"
FORM_HEADER = "Member Form"

# Button labels
BUTTON_QUIT = "Quit"
BUTTON_ADD = "Add"
BUTTON_SAVE = "Save"
BUTTON_BACK = "Back"
BUTTON_ADD_SOCIAL = "Add Social Network"
BUTTON_ADD_ALIAS = "Add Alias"
BUTTON_DELETE = "Delete"

# Input placeholders
PLACEHOLDER_NAME = "Name"
PLACEHOLDER_EMAIL = "Email"
PLACEHOLDER_CITY = "City"
PLACEHOLDER_HOMEPAGE = "Homepage"
PLACEHOLDER_SOCIAL_URL = "Social network URL"
PLACEHOLDER_ALIAS = "Alias"

# Section headers
SECTION_SOCIAL = "Social Networks"
SECTION_ALIASES = "Aliases"
SECTION_WHO = "Who are you and what do you do?"
SECTION_PYTHON = "How do you program in Python?"
SECTION_CONTRIB = "Do you have any contributions to the Python community?"
SECTION_AVAIL = "Are you available for mentoring, consulting, talks?"

# Messages
MESSAGE_PROMPT_FOR_GITHUB_TOKEN = (
    "Please enter your GitHub personal access token: "
)
MESSAGE_EXIT = "See you next time!"
MESSAGE_QUIT = "Exiting the application."
MESSAGE_FILE_READ_ERROR = "Error reading file {filename}: {error}"
MESSAGE_UNAUTHORIZED = "Unauthorized access. Please check your access token."
MESSAGE_REPO_NOT_FOUND = (
    "Repository not found. Please check your access token."
)
MESSAGE_FILE_EDITED_PR = (
    "File {name_file} edited, commit and changes sent to existing PR."
)
MESSAGE_FILE_SAVED_PR = "File {name_file} saved, commit and PR ready."
MESSAGE_CREATE_ENTRY = (
    "Creating a new entry to `blog/members` for {name} (alias: {first_alias})."
)
MESSAGE_CHANGE_ENTRY = (
    "Changing an entry to `blog/members` for {name} (alias: {first_alias})."
)
MESSAGE_LOAD_FILE_ERROR = "Error reading file {filename}: {error}"

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
