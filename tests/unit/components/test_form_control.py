import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input, Static

from edit_python_pe.components.form_control import FormControl


class FormControlTestApp(App):
    def compose(self) -> ComposeResult:
        yield FormControl(
            Input(id="test-input"), label="Test Label", help_text="Test Help"
        )


class TestFormControl:
    @pytest.mark.asyncio
    async def test_form_control_logic(self):
        app = FormControlTestApp()
        async with app.run_test():
            fc = app.query_one(FormControl)
            assert fc.label_text == "Test Label"
            assert fc.help_text_content == "Test Help"

            # Error states
            error_msg = fc.query_one(".form-error-text", Static)
            assert error_msg.display is False

            fc.show_error("Bad input")
            assert fc.has_class("has-error")
            assert error_msg.display is True
            assert str(error_msg.render()) == "Bad input"

            fc.clear_error()
            assert not fc.has_class("has-error")
            assert error_msg.display is False
            assert str(error_msg.render()) == ""
