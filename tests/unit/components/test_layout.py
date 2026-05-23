import pytest
from textual.app import App, ComposeResult

from edit_python_pe.components.layout import AppFooter, AppHeader


class ComponentTestApp(App):
    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield AppFooter()


class TestLayout:
    @pytest.mark.asyncio
    async def test_layout_rendering(self):
        app = ComponentTestApp()
        async with app.run_test():
            app.query_one(AppHeader)
            app.query_one(AppFooter)
