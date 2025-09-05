#!/bin/sh
uv run pybabel extract -F babel.cfg -o messages.pot .
uv run pybabel init -i messages.pot -d translations -l es
uv run pybabel init -i messages.pot -d translations -l it
uv run pybabel init -i messages.pot -d translations -l fr
echo "Translating..."
uv run ./bin/translate.py translations/es/LC_MESSAGES/messages.po es
uv run ./bin/translate.py translations/it/LC_MESSAGES/messages.po it
uv run ./bin/translate.py translations/fr/LC_MESSAGES/messages.po fr
uv run pybabel compile -d translations
echo "Done."
