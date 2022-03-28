from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import DefaultDict
import polib
from ._base import Command
from .._extractor import extract_messages, Message
from .._project import find_project_root, Project


class Generate(Command):
    """Generate a `.po` file for a language.
    """
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument('--path', type=Path, default=Path())
        parser.add_argument('--lang', default='en')
        now = datetime.now(timezone.utc).astimezone()
        parser.add_argument('--now', default=now.isoformat())

    def run(self) -> int:
        files: DefaultDict[Path, polib.POFile]
        files = defaultdict(polib.POFile)
        for msg in extract_messages(self.args.path):
            entry = self._msg_to_entry(msg)
            root = find_project_root(msg.path)
            files[root].append(entry)

        if not files:
            return 1
        now = datetime.fromisoformat(self.args.now).strftime("%F %H:%M%z")
        for root, po_file in files.items():
            project = Project(root)
            catalog = root / 'locales'
            catalog.mkdir(exist_ok=True)
            file_path = catalog / f'{self.args.lang}.po'
            po_file.metadata = {
                'Project-Id-Version': f'{project.name} {project.version}',
                'Report-Msgid-Bugs-To': project.bug_tracker,
                'POT-Creation-Date': now,
                'PO-Revision-Date': now,
                'Last-Translator': project.author,
                'Language-Team': project.author,
                'Language': self.args.lang,
                'MIME-Version': '1.0',
                'Content-Type': 'text/plain; charset=UTF-8',
                'Content-Transfer-Encoding': '8bit',
                'Plural-Forms': 'nplurals=2; plural=n == 1 ? 0 : 1;',
            }
            po_file.save(str(file_path))
        return 0

    def _msg_to_entry(self, msg: Message) -> polib.POEntry:
        return polib.POEntry(
            msgid=msg.text,
            msgstr='',
            occurrences=[(msg.file_name, msg.line)],
        )
