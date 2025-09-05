#!/usr/bin/env python3
import sys

import polib
from deep_translator import GoogleTranslator


def main(filename: str, language: str) -> None:
    po = polib.pofile(filename)
    translator = GoogleTranslator(source="en", target=language)

    for entry in po:
        entry.msgstr = translator.translate(entry.msgid)

    po.save(filename)


if __name__ == "__main__":
    main(*sys.argv[1:])
