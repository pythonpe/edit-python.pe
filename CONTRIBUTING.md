# Developer Guide

This document will explain how to contribute to the edit-python.pe project.

## How to Contribute

1. Make sure to find an open issue on [GitHub](https://github.com/python.pe/edit-python.pe/issues).
2. Fork the [edit-python.pe](https://github.com/python.pe/edit-python.pe) repository.
3. Clone the forked repository to your local machine.
4. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/).
5. Install dependencies:

```bash
uv sync
```

6. Install pre-commit hook:

```bash
uv run pre-commit install
```

7. Make your changes.
8. Cover your changes with tests.
9. Run the test coverage:

```bash
./test/test.sh
```

8. Commit your changes, if the pre-commit hook fails, run `./bin/test.sh` to
   know which test failed.
9. If the last step was your last commit on this issue, run this command:

```bash
uv run ./bin/bump-version.sh
```

10. Push your changes to the forked repository.
11. Open a pull request on [GitHub](https://github.com/python.pe/edit-python.pe/pulls).
