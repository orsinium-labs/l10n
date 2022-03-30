from argparse import ArgumentParser
from pathlib import Path

import polib
from googletrans import Translator

from .._project import Project, find_project_root
from ._base import Command


class Translate(Command):
    """Translate all text without translation using Google Translate.
    """
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--path', type=Path, default=Path(),
            help='the base directory from where to start project root lookup',
        )
        parser.add_argument(
            '--src-lang', default='en',
            help='the language used for messages',
        )

    def run(self) -> int:
        project_root = find_project_root(self.args.path)
        project = Project(project_root)
        translator = Translator()
        for po_path in project.po_root.iterdir():
            if po_path.suffix != '.po':
                continue
            print(po_path.stem)
            po_file = polib.pofile(str(po_path))
            for entry in po_file:
                if not entry.msgstr:
                    translation = translator.translate(
                        entry.msgid,
                        src=self.args.src_lang,
                        dest=po_file.metadata.get('Language', po_path.stem),
                    )
                    entry.msgstr = translation.text
                    if 'fuzzy' not in entry.flags:
                        entry.flags.append('fuzzy')
            po_file.save(str(po_path))
        return 0
