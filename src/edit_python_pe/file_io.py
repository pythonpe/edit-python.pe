import os

from .constants import AUTHORS_FILE


def _read_file(file_path: str) -> str:
    with open(file_path, encoding="utf-8") as fd:
        return fd.read()


def _append_file(file_content: str, file_path: str) -> None:
    dirpath = os.path.dirname(file_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as fd:
        fd.write(file_content)


def _write_file(file_content: str, file_path: str) -> None:
    dirpath = os.path.dirname(file_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as fd:
        fd.write(file_content)


def _write_authors_file(
    repo_path: str,
    aliases: list[str],
    name: str,
    email: str,
) -> None:
    file_path = os.path.join(repo_path, AUTHORS_FILE)

    try:
        contents = _read_file(file_path)
    except FileNotFoundError:
        contents = ""

    alias = aliases[0] if aliases else name
    candidate = f"{name}({alias}) <{email}>"
    normalized_lines = [line.strip() for line in contents.splitlines()]
    if candidate not in normalized_lines:
        _append_file(f"\n{candidate}", file_path)
