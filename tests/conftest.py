import gettext
from unittest.mock import MagicMock

import pytest


class DummyTranslation:
    def gettext(self, message):
        return message

    def install(self):
        import builtins

        builtins._ = self.gettext  # ty:ignore[unresolved-attribute]


@pytest.fixture(autouse=True)
def mock_gettext(monkeypatch):
    monkeypatch.setattr(
        gettext, "translation", lambda *args, **kwargs: DummyTranslation()
    )


@pytest.fixture
def mock_github_auth(monkeypatch):
    monkeypatch.setattr("edit_python_pe.github_client.Github", MagicMock())
    monkeypatch.setattr(
        "edit_python_pe.github_client.get_repo",
        MagicMock(return_value=("fake-token", MagicMock())),
    )
