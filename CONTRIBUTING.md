# 🛠️ Developer Guide

This document explains how to contribute to the edit-python.pe project, the commands needed for development, and the translation workflow.

## 🤝 How to Contribute

1. Make sure to find an open issue on [GitHub](https://github.com/pythonpe/edit-python.pe/issues).
1. Fork the [edit-python.pe](https://github.com/pythonpe/edit-python.pe) repository.
1. Clone the forked repository to your local machine.
1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/).
1. Install dependencies:

   ```bash
   uv sync
   ```

1. Install the pre-commit hooks (enforces conventional commits and quality checks):

   ```bash
   uv run pre-commit install --hook-type commit-msg
   uv run pre-commit install
   ```

1. Make your changes and cover them with tests.
1. Push your changes to the forked repository.
1. Open a pull request on [GitHub](https://github.com/pythonpe/edit-python.pe/pulls).

## 🚀 Development Commands

We use `poethepoet` (poe) as our task runner. Run the following commands as needed during development:

- `uv run poe lint`: Runs the `ruff` linter.
- `uv run poe lint:format`: Formats the code using `ruff format`.
- `uv run poe lint:types`: Checks types using `ty check`.
- `uv run poe lint:docs`: Lints Markdown files using `markdownlint` (excludes `CHANGELOG.md`).
- `uv run poe test`: Runs the test coverage with `pytest`.

## 📝 Commit Style (Conventional Commits)

This project enforces [Conventional Commits](https://www.conventionalcommits.org/) via a pre-commit hook powered by [Commitizen](https://commitizen-tools.github.io/commitizen/). Every commit message **must** follow this format:

```text
<type>(<optional scope>): <short description>
```

Allowed types:

| Type | When to use |
| ------- | ------------------------------------------------------------ |
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Code style changes (formatting, missing semicolons, etc.) |
| `refactor` | Code change that is neither a fix nor a feature |
| `perf` | A code change that improves performance |
| `test` | Adding or fixing tests |
| `build` | Changes to build system or dependencies |
| `ci` | Changes to CI configuration files and scripts |
| `chore` | Other changes that don't modify source or test files |

**Examples:**

```text
feat(auth): add GitHub OAuth login
fix(markdown): handle missing homepage field gracefully
docs: update README with uvx usage
```

You can use `uv run cz commit` as an interactive guided commit helper instead of `git commit`.

## 🏷️ Release Cycle

Releases are managed by [Commitizen](https://commitizen-tools.github.io/commitizen/), which automatically:

- Determines the next semantic version from the commit history (`feat` → minor bump, `fix` → patch bump, `feat!` or `BREAKING CHANGE` → major bump).
- Updates the version in `pyproject.toml` and `src/edit_python_pe/__version__.py`.
- Generates or appends to `CHANGELOG.md`.
- Creates a git tag `v<version>`.

### Performing a Release

> **Only maintainers** should run this command on the `main` branch.

```bash
uv run poe release
```

This runs `cz bump --changelog` under the hood. After the tag is created, push both the commit and the tag:

```bash
git push && git push --tags
```

### Previewing the Changelog

To regenerate or preview the full changelog without bumping the version:

```bash
uv run poe release:changelog
```

## 🌐 Translation Workflow

This project uses `pybabel` for translations, completely managed through `poe` tasks. The translation files are packaged internally within `src/edit_python_pe/locale/` so they are automatically included in PyPI wheel distributions.

### 1. Generating or Updating `.po` files

When you add new `_("...")` strings in the source code, run:

```bash
uv run poe messages:update
```

This automatically extracts all translation strings from `src/edit_python_pe/` into `messages.pot` and **updates all existing locales** (e.g. `es`, `fr`, etc.) with the new strings, keeping existing translations intact.

If you only want to extract strings to `messages.pot` without updating the language files, run:

```bash
uv run poe messages:extract
```

> **Note:** We have removed automated machine translation scripts. Automatic tools often miss context-specific terminology (for example, translating "Save" as "Ahorro" instead of "Guardar"). You **must** review the `.po` files one by one and translate them manually, ensuring the correct context for the application.

### 2. Compiling `.mo` files

After you finish manually translating the `.po` files, you must compile them into the binary `.mo` format so the application can read them.

```bash
uv run poe messages:compile
```

This command compiles all languages in the `locale` directory simultaneously.

---

### Adding a New Language

If you want to add an entirely new language (for example, German `de`), use the `messages:init` command:

```bash
uv run poe messages:init --lang de
```

This extracts the strings and initializes the completely new directory `src/edit_python_pe/locale/de/LC_MESSAGES/messages.po`.
