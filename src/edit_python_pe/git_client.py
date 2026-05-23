import os

import pygit2


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
    safe_name_file = os.path.basename(name_file)
    repo.index.add(f"blog/members/{safe_name_file}")
    repo.index.add("AUTHORS")
    repo.index.write()
    author_sig = pygit2.Signature(name or "Unknown", email or "unknown@email")
    tree_id = repo.index.write_tree()
    parents = [] if repo.head_is_unborn else [repo.head.target]
    commit_msg = f"Changed {name_file}" if was_changed else f"Added {name_file}"
    repo.create_commit(
        "HEAD",
        author_sig,
        author_sig,
        commit_msg,
        tree_id,
        parents,
    )

    callbacks = pygit2.callbacks.RemoteCallbacks(
        credentials=pygit2.UserPass(token, "x-oauth-basic")
    )
    remote = repo.remotes["origin"]
    remote.push([repo.head.name], callbacks=callbacks)
    return commit_msg, repo, remote, callbacks
