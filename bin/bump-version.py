#!/usr/bin/env python3
import tomllib
import subprocess

import tomli_w


def bump_version(version: str) -> str:
    splitted_version = version.split(".")
    bumped_version = int(splitted_version[-1]) + 1
    splitted_version[-1] = str(bumped_version)
    return ".".join(splitted_version)


def main() -> None:
    with open("uv.lock", "rb") as fd:
        data = tomllib.load(fd)

    package = next(p for p in data["package"] if p["name"] == "edit-python-pe")

    package["version"] = bump_version(package["version"])

    with open("pyproject.toml", "rb") as fd:
        data = tomllib.load(fd)

    data["project"]["version"] = package["version"]

    with open("pyproject.toml", "wb") as fd:
        tomli_w.dump(data, fd)

    subprocess.run(["git", "add", "pyproject.toml"])

    with open("uv.lock", "wb") as fd:
        tomli_w.dump(data, fd)

    subprocess.run(["git", "add", "uv.lock"])
    subprocess.run(["git", "commit", "-m", "Bump version"])


if __name__ == "__main__":
    main()
