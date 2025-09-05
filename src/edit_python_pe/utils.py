import getpass
import hashlib
import os
import re
from datetime import date, datetime
from time import sleep
from typing import TYPE_CHECKING

import pygit2
from github import Github
from github.GithubException import BadCredentialsException, GithubException
from github.Repository import Repository
from platformdirs import user_data_dir

if TYPE_CHECKING:
    from .main import MemberApp

from .strings import (MD_CONTENT, MESSAGE_FILE_EDITED_PR,
                      MESSAGE_FILE_SAVED_PR, MESSAGE_LOAD_FILE_ERROR,
                      MESSAGE_PROMPT_FOR_GITHUB_TOKEN, MESSAGE_REPO_NOT_FOUND,
                      MESSAGE_UNAUTHORIZED)


def _compute_file_name(aliases: list[str], name: str, email: str) -> str:
    # compute name_file
    if aliases:
        alias_for_name = aliases[0].lower().replace(" ", "_")
    else:
        alias_for_name = name.lower().replace(" ", "_")

    sha_hash = hashlib.sha1(
        (alias_for_name + email + datetime.now().isoformat()).encode("utf-8")
    ).hexdigest()[:8]
    return f"{alias_for_name}-{sha_hash}.md"


def _read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as fd:
        return fd.read()


def _append_file(file_content: str, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as fd:
        fd.write(file_content)


def _write_file(file_content: str, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as fd:
        fd.write(file_content)


def _commit_and_push(
    repo_path: str,
    token: str,
    was_changed: bool,
    name_file: str,
    name: str,
    email: str,
) -> tuple[
    str,
    pygit2.repository.Repository,
    pygit2.remotes.Remote,
    pygit2.callbacks.RemoteCallbacks,
]:
    repo = pygit2.repository.Repository(repo_path)
    repo.index.add_all()
    repo.index.write()
    author_sig = pygit2.Signature(name or "Unknown", email or "unknown@email")
    tree_id = repo.index.write_tree()
    parents = [] if repo.head_is_unborn else [repo.head.target]
    commit_msg = (
        f"Changed {name_file}" if was_changed else f"Added {name_file}"
    )
    repo.create_commit(
        "HEAD", author_sig, author_sig, commit_msg, tree_id, parents
    )

    callbacks = pygit2.callbacks.RemoteCallbacks(
        credentials=pygit2.UserPass(token, "x-oauth-basic")
    )
    remote = repo.remotes["origin"]
    remote.push([repo.head.name], callbacks=callbacks)
    return commit_msg, repo, remote, callbacks


def _create_member_file(
    file_content: str,
    current_file: str | None,
    repo_path: str,
    aliases: list[str],
    name: str,
    email: str,
) -> tuple[str, str]:
    # Name the file
    name_file = (
        current_file
        if current_file is not None
        else _compute_file_name(aliases, name, email)
    )

    # Write file
    file_path = os.path.join(repo_path, "blog", "members", name_file)
    _write_file(file_content, file_path)
    return name_file, file_path


def _write_authors_file(
    repo_path: str, aliases: list[str], name: str, email: str
):
    file_path = os.path.join(repo_path, "AUTHORS")
    contents = _read_file(file_path)
    file_content = f"\n{name}({_get_alias(aliases, name)}) <{email}>"
    if file_content.strip() not in contents:
        _append_file(file_content, file_path)


def _get_alias(aliases: list[str], name: str) -> str:
    if aliases:
        return aliases[0]
    return name


def get_repo() -> tuple[str, Repository]:
    token = getpass.getpass(MESSAGE_PROMPT_FOR_GITHUB_TOKEN)
    g = Github(token)

    try:
        return token, g.get_repo("pythonpe/python.pe")
    except BadCredentialsException:
        print(MESSAGE_UNAUTHORIZED)
        exit(1)
    except GithubException:
        print(MESSAGE_REPO_NOT_FOUND)
        exit(1)


def fork_repo(token: str, original_repo: Repository) -> tuple[str, Repository]:
    forked_repo = original_repo.create_fork()
    forked_repo_url = forked_repo.clone_url
    repo_path = user_data_dir(appname="edit-python-pe", appauthor="python.pe")

    if not os.path.exists(repo_path):
        callbacks = pygit2.callbacks.RemoteCallbacks(
            credentials=pygit2.UserPass(token, "x-oauth-basic")
        )
        sleep(3)
        pygit2.clone_repository(
            forked_repo_url, repo_path, callbacks=callbacks
        )
    return repo_path, forked_repo


def create_pr(
    file_content: str,
    current_file: str | None,
    repo_path: str,
    original_repo: Repository,
    forked_repo: Repository,
    token: str,
    aliases: list[str],
    name: str,
    email: str,
) -> str:
    name_file, file_path = _create_member_file(
        file_content, current_file, repo_path, aliases, name, email
    )
    _write_authors_file(repo_path, aliases, name, email)

    # commit & push
    commit_msg, repo, remote, callbacks = _commit_and_push(
        repo_path,
        token,
        current_file is not None,
        name_file,
        name,
        email,
    )

    # PR logic
    pr_title = commit_msg
    first_alias = aliases[0] if aliases else ""
    pr_body = (
        f"Changing an entry to `blog/members` for {name} (alias: {first_alias})."
        if current_file
        else f"Creating a new entry to `blog/members` for {name} (alias: {first_alias})."
    )
    fork_owner = forked_repo.owner.login
    head_branch = f"{fork_owner}:main"
    base_branch = "main"

    # If editing, retrieve PR by title and push to its branch
    if current_file:
        # Try to find an open PR with matching title
        prs = original_repo.get_pulls(
            state="open", sort="created", base=base_branch
        )
        pr_found = None
        for pr in prs:
            if current_file in pr.title:
                pr_found = pr
                break
        if pr_found:
            # Push to the PR branch (simulate, as actual branch logic may differ)
            remote.push([repo.head.name], callbacks=callbacks)
            return MESSAGE_FILE_EDITED_PR.format(name_file=name_file)
        else:
            original_repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=head_branch,
                base=base_branch,
            )
            return MESSAGE_FILE_SAVED_PR.format(name_file=name_file)
    else:
        original_repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=head_branch,
            base=base_branch,
        )
        return MESSAGE_FILE_SAVED_PR.format(name_file=name_file)


def load_file_into_form(app: "MemberApp", filename: str) -> None:
    path_md = os.path.join(app.repo_path, "blog", "members", filename)
    if not os.path.exists(path_md):
        return
    try:
        content = _read_file(path_md)
    except Exception as e:
        app.exit(
            message=MESSAGE_LOAD_FILE_ERROR.format(filename=filename, error=e)
        )
        return

    app.clear_form()

    # Extract YAML frontmatter
    yaml_match = re.search(r"---\n(.*?)---\n", content, re.DOTALL)
    yaml_data = {}
    if yaml_match:
        try:
            import yaml

            yaml_data = yaml.safe_load(yaml_match.group(1))
        except Exception:
            yaml_data = {}
    app.name_input.value = yaml_data.get("author", "")
    app.city_input.value = yaml_data.get("location", "")

    # Extract member name from first markdown header
    name_match = re.search(r"^# (.+)", content, re.MULTILINE)
    if name_match:
        app.name_input.value = name_match.group(1).strip()

    # Extract gravatar email
    gravatar_match = re.search(r"```\{gravatar\} ([^\n]+)", content)
    if gravatar_match:
        app.email_input.value = gravatar_match.group(1).strip()

    # Extract social links from raw HTML block
    social_block = re.search(r"```\{raw\} html\n(.*?)```", content, re.DOTALL)
    if social_block:
        social_html = social_block.group(1)
        social_link_pattern = re.compile(
            r'<a[^>]*href="([^"]+)"[^>]*>\s*<iconify-icon[^>]*icon="simple-icons:([^"]+)"',
            re.DOTALL,
        )
        for match in social_link_pattern.finditer(social_html):
            url = match.group(1)
            platform = match.group(2)
            app.add_social_entry()
            last_entry = app.social_entries[-1]
            last_entry.select.value = platform
            last_entry.url_input.value = url

    # Extract aliases, city, homepage from colon-prefixed lines
    alias_match = re.search(r":Aliases:\s*([^\n]+)", content)
    if alias_match:
        aliases = [a.strip() for a in alias_match.group(1).split(",")]
        for alias_val in aliases:
            app.add_alias_entry()
            app.alias_entries[-1].alias_input.value = alias_val
    city_match = re.search(r":Ciudad:\s*([^\n]+)", content)
    if city_match:
        app.city_input.value = city_match.group(1).strip()
    homepage_match = re.search(r":Homepage:\s*([^\n]+)", content)
    if homepage_match:
        app.homepage_input.value = homepage_match.group(1).strip()

    # Extract markdown sections under headers
    who_match = re.search(
        r"### ¿Quién eres y a qué te dedicas\?\n(.*?)(?=^### |\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if who_match:
        app.who_area.text = who_match.group(1).strip()
    python_match = re.search(
        r"### ¿Cómo programas en Python\?\n(.*?)(?=^### |\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if python_match:
        app.python_area.text = python_match.group(1).strip()
    contrib_match = re.search(
        r"### ¿Tienes algún aporte a la comunidad de Python\?\n(.*?)(?=^### |\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if contrib_match:
        app.contributions_area.text = contrib_match.group(1).strip()
    avail_match = re.search(
        r"### ¿Estás disponible para hacer mentoring, consultorías, charlas\?\n(.*?)(?=^### |\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if avail_match:
        app.availability_area.text = avail_match.group(1).strip()


def build_md_content(
    name: str,
    email: str,
    aliases: list[str],
    socials: list[tuple[str, str]],
    city: str,
    homepage: str,
    who: str,
    python_: str,
    contributions: str,
    availability: str,
) -> str:
    md_lines = [
        MD_CONTENT["yaml_start"],
        MD_CONTENT["yaml_blogpost"],
        MD_CONTENT["yaml_date"].format(
            date=date.today().strftime("%d %b, %Y")
        ),
        MD_CONTENT["yaml_author"].format(author=_get_alias(aliases, name)),
        MD_CONTENT["yaml_location"].format(city=city),
        MD_CONTENT["yaml_category"],
        MD_CONTENT["yaml_language"],
        MD_CONTENT["yaml_image"],
        MD_CONTENT["yaml_excerpt"],
        MD_CONTENT["yaml_end"],
        "",
        MD_CONTENT["header_name"].format(name=name),
        "",
        MD_CONTENT["gravatar_block"].format(email=email),
        "",
    ]
    if socials:
        md_lines.append(MD_CONTENT["social_block_start"])
        md_lines.append(MD_CONTENT["social_ul_start"])
        for plat, url in socials:
            md_lines.append(
                MD_CONTENT["social_li"].format(platform=plat, url=url)
            )
        md_lines.append(MD_CONTENT["social_ul_end"])
        md_lines.append(MD_CONTENT["social_block_end"])
        md_lines.append("")

    if aliases:
        md_lines.append(
            MD_CONTENT["aliases"].format(aliases=", ".join(aliases))
        )
        md_lines.append("")

    if city:
        md_lines.append(MD_CONTENT["city"].format(city=city))
        md_lines.append("")

    if homepage:
        md_lines.append(MD_CONTENT["homepage"].format(homepage=homepage))
        md_lines.append("")

    md_lines.append(MD_CONTENT["section_about"])
    md_lines.append("")

    if who:
        md_lines.append(MD_CONTENT["section_who"])
        md_lines.append("")
        md_lines.append(who)
        md_lines.append("")

    if python_:
        md_lines.append(MD_CONTENT["section_python"])
        md_lines.append("")
        md_lines.append(python_)
        md_lines.append("")

    if contributions:
        md_lines.append(MD_CONTENT["section_contrib"])
        md_lines.append("")
        md_lines.append(contributions)
        md_lines.append("")

    if availability:
        md_lines.append(MD_CONTENT["section_avail"])
        md_lines.append("")
        md_lines.append(availability)
        md_lines.append("")

    return "\n".join(md_lines)
