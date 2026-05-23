from textual.containers import Horizontal
from textual.types import NoSelection
from textual.widgets import Button, Input, Select

from ..constants import (
    BITBUCKET_OPTION,
    FACEBOOK_OPTION,
    GITHUB_OPTION,
    GITLAB_OPTION,
    INSTAGRAM_OPTION,
    LINKEDIN_OPTION,
    X_OPTION,
    YOUTUBE_OPTION,
)
from ..strings import _
from .form_control import FormControl


class SocialEntry(FormControl):
    def __init__(self, index: int, value: str | NoSelection) -> None:
        self.index = index
        self.select = Select(
            options=[
                GITHUB_OPTION,
                GITLAB_OPTION,
                BITBUCKET_OPTION,
                LINKEDIN_OPTION,
                FACEBOOK_OPTION,
                INSTAGRAM_OPTION,
                X_OPTION,
                YOUTUBE_OPTION,
            ],
            prompt=_("Social Network"),
            value=value,
        )
        self.url_input = Input(placeholder=_("Social network URL"))
        self.delete_btn = Button(
            _("Delete"), id=f"delete_social_{index}", variant="error"
        )

        super().__init__(
            Horizontal(
                self.select,
                self.url_input,
                self.delete_btn,
                classes="entry-row",
            )
        )
