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
            help='the language used for messages (msgid)',
        )

    def run(self) -> int:
        project_root = find_project_root(self.args.path)
        project = Project(project_root)
        translator = Translator()
        for po_path in project.po_root.iterdir():
            if po_path.suffix != '.po':
                continue
            self.print(po_path.stem)
            translated = 0
            po_file = polib.pofile(str(po_path))
            dest_lang = po_file.metadata.get('Language', po_path.stem)
            dest_lang = dest_lang.split('_')[0]
            dest_lang = dest_lang.split('-')[0]
            for entry in po_file:
                if entry.msgstr:
                    continue
                translation = translator.translate(
                    entry.msgid,
                    src=self.args.src_lang,
                    dest=dest_lang,
                )
                entry.msgstr = translation.text
                if 'fuzzy' not in entry.flags:
                    entry.flags.append('fuzzy')
                translated += 1
            po_file.save()
            self.print(f'  translated: {translated}')
        return 0
