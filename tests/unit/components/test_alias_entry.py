import pytest
from textual.app import App, ComposeResult

from edit_python_pe.components.alias_entry import AliasEntry


class AliasEntryTestApp(App):
    def compose(self) -> ComposeResult:
        yield AliasEntry(1)


class TestAliasEntry:
    @pytest.mark.asyncio
    async def test_alias_entry_logic(self):
        app = AliasEntryTestApp()
        async with app.run_test():
            alias = app.query_one(AliasEntry)
            assert alias.index == 1
            assert alias.alias_input.placeholder == "Alias"
