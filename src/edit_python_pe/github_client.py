import logging
import os
import random
import shutil
from time import sleep

import pygit2
from github import Auth, Github
from github.GithubException import BadCredentialsException, GithubException
from github.Repository import Repository
from platformdirs import user_data_dir

from .file_io import _write_authors_file
from .git_client import _commit_and_push
from .markdown_builder import _create_member_file
from .strings import _

logger = logging.getLogger(__name__)


def get_repo(token: str) -> tuple[str, Repository]:
    auth = Auth.Token(token)
    g = Github(auth=auth)

    try:
        return token, g.get_repo("pythonpe/python.pe")
    except BadCredentialsException as err:
        raise ValueError(
            _("Unauthorized access. Please check your access token.")
        ) from err
    except GithubException as err:
        raise ValueError(
            _("Repository not found. Please check your access token.")
        ) from err


def fork_repo(token: str, original_repo: Repository) -> tuple[str, Repository]:
    forked_repo = original_repo.create_fork()
    forked_repo_url = forked_repo.clone_url
    repo_path = user_data_dir(appname="edit-python-pe", appauthor="python.pe")

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, ignore_errors=True)

    callbacks = pygit2.callbacks.RemoteCallbacks(
        credentials=pygit2.UserPass(token, "x-oauth-basic")
    )

    max_retries = 5
    for attempt in range(max_retries):
        try:
            pygit2.clone_repository(forked_repo_url, repo_path, callbacks=callbacks)
            break
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(
                    "Failed to clone forked repository after %d attempts", max_retries
                )
                raise
            sleep_time = 2**attempt + random.uniform(0, 1)  # noqa: S311
            logger.warning(
                "Attempt %d to clone repository failed: %s. Retrying in %.2fs...",
                attempt + 1,
                e,
                sleep_time,
            )
            sleep(sleep_time)

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
) -> tuple[str, str | None]:
    name_file, _unused_file_path = _create_member_file(
        file_content,
        current_file,
        repo_path,
        aliases,
        name,
        email,
    )
    _write_authors_file(
        repo_path,
        aliases,
        name,
        email,
    )

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
        else (
            f"Creating a new entry to `blog/members` for {name} (alias: {first_alias})."
        )
    )
    fork_owner = forked_repo.owner.login
    head_branch = f"{fork_owner}:main"
    base_branch = "main"

    pr_url = None

    # If editing, retrieve PR by title and push to its branch
    if current_file:
        # Try to find an open PR with matching title
        prs = original_repo.get_pulls(
            state="open", sort="created", base=base_branch, head=head_branch
        )
        pr_found = None
        for pr in prs:
            if pr.title.endswith(current_file):
                pr_found = pr
                break
        if pr_found:
            # Push to the PR branch
            remote.push([repo.head.name], callbacks=callbacks)
            pr_url = pr_found.html_url
            return (
                _(
                    "Woohoo! Changes to {name_file} were successfully sent to your "
                    "existing PR! 🎉"
                ).format(name_file=name_file),
                pr_url,
            )
        else:
            pr = original_repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=head_branch,
                base=base_branch,
            )
            pr_url = pr.html_url
            return (
                _(
                    "Woohoo! {name_file} was saved successfully and "
                    "your new PR is ready! 🎉"
                ).format(name_file=name_file),
                pr_url,
            )
    else:
        pr = original_repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=head_branch,
            base=base_branch,
        )
        pr_url = pr.html_url
        return (
            _(
                "Woohoo! {name_file} was saved successfully and "
                "your new PR is ready! 🎉"
            ).format(name_file=name_file),
            pr_url,
        )
