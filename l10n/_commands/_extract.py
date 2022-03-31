from __future__ import annotations
from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import polib
import l10n

from .._extractor import Message, extract_messages
from .._project import Project, find_project_root
from ._base import Command
from .._plurals import PLURALS, GERMANIC


class Extract(Command):
    """Generate a `.po` file for a language based on messages in the code.
    """
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument('--path', type=Path, default=Path())
        parser.add_argument('--lang', default='en')
        now = datetime.now(timezone.utc).astimezone()
        parser.add_argument('--now', default=now.isoformat())

    def run(self) -> int:
        files: defaultdict[Path, polib.POFile]
        files = defaultdict(polib.POFile)
        for msg in extract_messages(self.args.path):
            entry = self._msg_to_entry(msg)
            root = find_project_root(msg.path)
            files[root].append(entry)

        if not files:
            self.print('No entries found')
            return 1
        now = datetime.fromisoformat(self.args.now).strftime("%F %H:%M%z")
        for root, po_file in files.items():
            lang: str = self.args.lang
            project = Project(root)
            project.po_root.mkdir(exist_ok=True)
            file_path = project.po_root / f'{lang}.po'
            plurals = PLURALS.get(lang, GERMANIC)
            po_file.metadata = {
                'Project-Id-Version': f'{project.name} {project.version}',
                'Report-Msgid-Bugs-To': project.bug_tracker,
                'POT-Creation-Date': now,
                'PO-Revision-Date': now,
                'Last-Translator': project.author,
                'Language-Team': project.author,
                'Language': lang,
                'MIME-Version': '1.0',
                'Content-Type': 'text/plain; charset=UTF-8',
                'Content-Transfer-Encoding': '8bit',
                'Plural-Forms': str(plurals),
                'Generated-By': f'l10n {l10n.__version__}',
            }
            po_file.save(str(file_path))
        return 0

    def _msg_to_entry(self, msg: Message) -> polib.POEntry:
        return polib.POEntry(
            msgid=msg.text,
            msgstr='',
            occurrences=[(msg.file_name, msg.line)],
        )
