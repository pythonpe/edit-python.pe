from edit_python_pe.strings import _, set_language


class TestStrings:
    def test_strings_set_language(self, monkeypatch):
        # Undo the autouse fixture from conftest.py that mocks gettext
        monkeypatch.undo()
        try:
            set_language("es")
            assert _("Quit") == "Abandonar"
        finally:
            set_language("en")
