import pytest
from textual.app import App, ComposeResult

from edit_python_pe.components.social_entry import SocialEntry


class SocialEntryTestApp(App):
    def compose(self) -> ComposeResult:
        yield SocialEntry(1, "github")


class TestSocialEntry:
    @pytest.mark.asyncio
    async def test_social_entry_logic(self):
        app = SocialEntryTestApp()
        async with app.run_test():
            social = app.query_one(SocialEntry)
            assert social.index == 1
            assert social.select.value == "github"
            assert social.url_input.placeholder == "Social network URL"
