#!/usr/bin/env python3
import subprocess


def main() -> None:
    subprocess.run(["uv", "version", "--bump", "patch"])
    result = subprocess.run(
        ["uv", "version", "--short"], stdout=subprocess.PIPE, encoding="utf-8"
    )
    version = result.stdout.strip()
    subprocess.run(["git", "add", "uv.lock"])
    subprocess.run(["git", "add", "pyproject.toml"])
    subprocess.run(["git", "commit", "-m", f"bump version to {version}"])
    subprocess.run(["git", "tag", f"v{version}"])
    subprocess.run(["git", "push", "--tags"])


if __name__ == "__main__":
    main()
