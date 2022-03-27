from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict
import polib
from ._base import Command
from .._extractor import extract_messages, Message


class Generate(Command):
    """Generate a `.po` file for a language.
    """
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument('--path', type=Path, default=Path())
        parser.add_argument('--lang', default='en')

    def run(self) -> int:
        files: DefaultDict[Path, polib.POFile]
        files = defaultdict(polib.POFile)
        for msg in extract_messages(self.args.path):
            entry = self._msg_to_entry(msg)
            root = self._find_project_root(msg.path)
            files[root].append(entry)
        for root, po_file in files.items():
            catalog = root / 'locales'
            catalog.mkdir(exist_ok=True)
            file_path = catalog / f'{self.args.lang}.po'
            po_file.save(str(file_path))
        return 0

    def _msg_to_entry(self, msg: Message) -> polib.POEntry:
        return polib.POEntry(
            msgid=msg.text,
            msgstr='',
            comment=f'{msg.location}',
        )

    def _find_project_root(self, file_path: Path) -> Path:
        for dir_path in file_path.parents:
            if (dir_path / 'pyproject.toml').exists():
                return dir_path
        for dir_path in file_path.parents:
            if (dir_path / '__init__.py').exists():
                continue
            return dir_path
        return Path()
