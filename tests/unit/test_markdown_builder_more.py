from unittest.mock import MagicMock, patch

from edit_python_pe.markdown_builder import (
    build_md_content,
    load_file_into_form,
)


class TestMarkdownBuilderMore:
    def test_build_md_content(self):
        name = "Test Name"
        email = "test@email.com"
        aliases = ["alias1"]
        socials = [
            ("github", "https://github.com/test"),
            ("twitter", "https://twitter.com/test"),
        ]
        city = "Lima"
        homepage = "https://example.com"
        who = "Developer"
        python_ = "Backend"
        contributions = "Code"
        availability = "Yes"

        content = build_md_content(
            name,
            email,
            aliases,
            socials,
            city,
            homepage,
            who,
            python_,
            contributions,
            availability,
        )
        assert "# Test Name" in content
        assert "{gravatar} test@email.com" in content
        assert "blogpost: true" in content
        assert "alias1" in content
        assert "github" in content
        assert "Lima" in content
        assert "Developer" in content
        assert "¿Quién eres y a qué te dedicas?" in content

    @patch("edit_python_pe.markdown_builder.os.path.exists")
    @patch("edit_python_pe.markdown_builder._read_file")
    def test_load_file_into_form(self, mock_read_file, mock_exists):
        mock_exists.return_value = True
        content = """---
blogpost: true
author: alias1
location: Lima
---

# Test Name

```{gravatar} test@email.com
---
width: 200
class: "member-gravatar"
---
```

```{raw} html
<ul class="social-media profile">
    <li>
        <a class="external reference" href="https://github.com/test">
            <iconify-icon icon="simple-icons:github" style="font-size:2em"></iconify-icon>
        </a>
    </li>
</ul>
```

:Aliases: alias1

:Ciudad: Lima

:Homepage: https://example.com

## Sobre mí

### ¿Quién eres y a qué te dedicas?

Developer

### ¿Cómo programas en Python?

Backend

### ¿Tienes algún aporte a la comunidad de Python?

Code

### ¿Estás disponible para hacer mentoring, consultorías, charlas?

Yes
"""
        mock_read_file.return_value = content
        mock_screen = MagicMock()
        mock_screen.social_entries = []
        mock_screen.alias_entries = []
        mock_screen.app.mount = MagicMock()

        # We must add an entry when `add_social_entry` is called to emulate real
        # behavior
        def mock_add_social(platform):
            entry = MagicMock()
            mock_screen.social_entries.append(entry)

        mock_screen.add_social_entry.side_effect = mock_add_social

        def mock_add_alias():
            entry = MagicMock()
            mock_screen.alias_entries.append(entry)

        mock_screen.add_alias_entry.side_effect = mock_add_alias

        load_file_into_form(mock_screen, "fake.md")

        assert mock_screen.name_input.value == "Test Name"
        assert mock_screen.email_input.value == "test@email.com"
        assert mock_screen.city_input.value == "Lima"
        assert mock_screen.homepage_input.value == "https://example.com"
        assert mock_screen.who_area.text == "Developer"
        assert mock_screen.python_area.text == "Backend"
        assert mock_screen.contributions_area.text == "Code"
        assert mock_screen.availability_area.text == "Yes"

        # Assert aliases were added
        mock_screen.add_alias_entry.assert_called()
        assert len(mock_screen.alias_entries) == 1
        assert mock_screen.alias_entries[0].alias_input.value == "alias1"

        # Assert socials were added
        mock_screen.add_social_entry.assert_called_with("github")
        assert len(mock_screen.social_entries) == 1
        assert (
            mock_screen.social_entries[0].url_input.value == "https://github.com/test"
        )

    @patch("edit_python_pe.markdown_builder.os.path.exists")
    def test_load_file_into_form_not_exists(self, mock_exists):
        mock_exists.return_value = False
        mock_screen = MagicMock()
        load_file_into_form(mock_screen, "fake.md")
        # Should return early
        mock_screen.app.exit.assert_not_called()

    @patch("edit_python_pe.markdown_builder.os.path.exists")
    @patch("edit_python_pe.markdown_builder._read_file")
    def test_load_file_into_form_read_error(self, mock_read, mock_exists):
        mock_exists.return_value = True
        mock_read.side_effect = Exception("Read error")
        mock_screen = MagicMock()
        load_file_into_form(mock_screen, "fake.md")
        mock_screen.app.exit.assert_called_once()
