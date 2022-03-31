from __future__ import annotations

from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import polib

import l10n

from .._extractor import Message, extract_messages
from .._plurals import GERMANIC, PLURALS
from .._project import Project, find_project_root
from ._base import Command


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
        for root, po_file in files.items():
            project = Project(root)
            project.po_root.mkdir(exist_ok=True)
            file_path = project.po_root / f'{self.args.lang}.po'

            if file_path.exists():
                old_file = polib.pofile(str(file_path))
                old_file.merge(po_file)
                po_file = old_file

            self._set_meta(project, po_file)
            po_file.save(str(file_path))
        return 0

    def _msg_to_entry(self, msg: Message) -> polib.POEntry:
        return polib.POEntry(
            msgid=msg.text,
            msgstr='',
            occurrences=[(msg.file_name, msg.line)],
        )

    def _set_meta(self, project: Project, po_file: polib.POFile) -> None:
        now = datetime.fromisoformat(self.args.now).strftime('%F %H:%M%z')
        lang: str = self.args.lang
        plurals = PLURALS.get(lang, GERMANIC)

        po_file.metadata['Project-Id-Version'] = f'{project.name} {project.version}'
        po_file.metadata.setdefault('Report-Msgid-Bugs-To', project.bug_tracker)
        po_file.metadata.setdefault('POT-Creation-Date', now)
        po_file.metadata['PO-Revision-Date'] = now
        po_file.metadata.setdefault('Last-Translator', project.author)
        po_file.metadata.setdefault('Language-Team', project.author)
        po_file.metadata.setdefault('Language', lang)
        po_file.metadata.setdefault('MIME-Version', '1.0')
        po_file.metadata.setdefault('Content-Type', 'text/plain; charset=UTF-8')
        po_file.metadata.setdefault('Content-Transfer-Encoding', '8bit')
        po_file.metadata.setdefault('Plural-Forms', str(plurals))
        po_file.metadata['Generated-By'] = f'l10n {l10n.__version__}'
