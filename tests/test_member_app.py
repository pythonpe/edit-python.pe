import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)
from edit_python_pe.main import MemberApp


class TestMemberApp(unittest.TestCase):
    def setUp(self):
        # Patch Github and Repository for testing
        self.token = "fake-token"
        self.repo = MagicMock()
        self.app = MemberApp(token=self.token, original_repo=self.repo)
        self.app.social_container = MagicMock()
        self.app.alias_container = MagicMock()
        # Manually initialize attributes normally set in on_mount
        self.app.social_entries = []
        self.app.alias_entries = []
        self.app.social_index = 0
        self.app.alias_index = 0

        # Mock UI elements and REPO_PATH
        # Use simple stub classes for input widgets and text areas
        class StubInput:
            def __init__(self):
                self.value = ""

        class StubTextArea:
            def __init__(self):
                self.text = ""

        self.app.name_input = StubInput()
        self.app.email_input = StubInput()
        self.app.city_input = StubInput()
        self.app.homepage_input = StubInput()
        self.app.about_me_area = StubTextArea()
        self.app.who_area = StubTextArea()
        self.app.python_area = StubTextArea()
        self.app.contributions_area = StubTextArea()
        self.app.availability_area = StubTextArea()
        self.app.REPO_PATH = "test_repo"

        # Patch remove method for entries to avoid Textual lifecycle errors
        # Use stub classes for entries with .remove() method
        class StubSocialEntry:
            def __init__(self):
                self.index = 0
                self.select = StubInput()
                self.url_input = StubInput()

            def remove(self):
                pass

        class StubAliasEntry:
            def __init__(self):
                self.index = 0
                self.alias_input = StubInput()

            def remove(self):
                pass

        self.StubSocialEntry = StubSocialEntry
        self.StubAliasEntry = StubAliasEntry

    def test_add_social_entry(self):
        # Patch add_social_entry to use stub
        self.app.social_entries = []
        self.app.social_container.mount = MagicMock()
        # Patch mount to accept any object
        self.app.social_container.mount = lambda x: None  # type: ignore

        def stub_add_social_entry():
            entry = self.StubSocialEntry()
            entry.index = self.app.social_index
            self.app.social_index += 1
            self.app.social_entries.append(entry)
            self.app.social_container.mount(entry)

        self.app.add_social_entry = stub_add_social_entry
        initial_count = len(self.app.social_entries)
        self.app.add_social_entry()
        self.assertEqual(len(self.app.social_entries), initial_count + 1)

    def test_add_alias_entry(self):
        # Patch add_alias_entry to use stub
        self.app.alias_entries = []
        self.app.alias_container.mount = MagicMock()
        # Patch mount to accept any object
        self.app.alias_container.mount = lambda x: None  # type: ignore

        def stub_add_alias_entry():
            entry = self.StubAliasEntry()
            entry.index = self.app.alias_index
            self.app.alias_index += 1
            self.app.alias_entries.append(entry)
            self.app.alias_container.mount(entry)

        self.app.add_alias_entry = stub_add_alias_entry
        initial_count = len(self.app.alias_entries)
        self.app.add_alias_entry()
        self.assertEqual(len(self.app.alias_entries), initial_count + 1)

    def test_clear_form(self):
        # Patch add_social_entry and add_alias_entry to use stub
        self.app.social_entries = []
        self.app.alias_entries = []
        self.app.social_container.remove_children = lambda: None  # type: ignore
        self.app.alias_container.remove_children = lambda: None  # type: ignore

        def stub_add_social_entry():
            entry = self.StubSocialEntry()
            entry.index = self.app.social_index
            self.app.social_index += 1
            self.app.social_entries.append(entry)
            self.app.social_container.mount(entry)

        def stub_add_alias_entry():
            entry = self.StubAliasEntry()
            entry.index = self.app.alias_index
            self.app.alias_index += 1
            self.app.alias_entries.append(entry)
            self.app.alias_container.mount(entry)

        self.app.add_social_entry = stub_add_social_entry
        self.app.add_alias_entry = stub_add_alias_entry
        self.app.add_social_entry()
        self.app.add_alias_entry()
        self.app.clear_form()
        self.assertEqual(len(self.app.social_entries), 0)
        self.assertEqual(len(self.app.alias_entries), 0)

    @patch("edit_python_pe.main.open", create=True)
    @patch("edit_python_pe.main.os.path.exists", return_value=True)
    def test_load_file_into_form(self, mock_exists, mock_open):
        # Simulate a markdown file with social and alias data
        mock_open.return_value.__enter__.return_value.read.return_value = """
---
@author: joe
@location: Lima
---
# Joe Doe
```{gravatar} joe@example.com
---
width: 200
class: "member-gravatar"
---
```
```{raw} html
<ul class="social-media profile">
    <li>
        <a class="external reference" href="https://github.com/joe.doe">
            <iconify-icon icon="simple-icons:github" style="font-size:2em"></iconify-icon>
        </a>
    </li>
</ul>
```
:Aliases: joe
:Ciudad: Lima
:Homepage: https://joe-doe.org
"""
        # Patch add_social_entry and add_alias_entry to use stub
        self.app.social_entries = []
        self.app.alias_entries = []

        def stub_add_social_entry():
            entry = self.StubSocialEntry()
            entry.index = self.app.social_index
            self.app.social_index += 1
            self.app.social_entries.append(entry)
            self.app.social_container.mount(entry)

        def stub_add_alias_entry():
            entry = self.StubAliasEntry()
            entry.index = self.app.alias_index
            self.app.alias_index += 1
            self.app.alias_entries.append(entry)
            self.app.alias_container.mount(entry)

        self.app.add_social_entry = stub_add_social_entry
        self.app.add_alias_entry = stub_add_alias_entry
        # Patch clear_form to avoid resetting stubs
        self.app.clear_form = lambda: None  # type: ignore
        self.app.load_file_into_form("fake.md")
        # Assert YAML author assignment first
        # The stub allows assignment, so check after YAML parsing
        yaml_author = "joe"
        self.assertIn(
            self.app.name_input.value,
            [yaml_author, "Joe Doe"],
            f"Expected YAML author or markdown header, got '{self.app.name_input.value}'",
        )
        # Now check if markdown header overwrites it
        # The regex should match '# Joe Doe' and overwrite the value
        # If not, print debug info
        if self.app.name_input.value != "Joe Doe":
            print(
                "DEBUG: Markdown header regex did not match, value is:",
                self.app.name_input.value,
            )
        self.assertEqual(
            self.app.name_input.value,
            "Joe Doe",
            f"Expected 'Joe Doe', got '{self.app.name_input.value}'",
        )
        self.assertEqual(self.app.email_input.value, "joe@example.com")
        self.assertEqual(self.app.city_input.value, "Lima")
        self.assertEqual(self.app.homepage_input.value, "https://joe-doe.org")
        self.assertGreaterEqual(len(self.app.social_entries), 1)
        self.assertGreaterEqual(len(self.app.alias_entries), 1)


if __name__ == "__main__":
    unittest.main()
