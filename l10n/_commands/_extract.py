from __future__ import annotations

from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

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
        parser.add_argument('--lang')
        now = datetime.now(timezone.utc).astimezone()
        parser.add_argument('--now', default=now.isoformat())

    def run(self) -> int:
        files: defaultdict[Path, list[polib.POEntry]]
        files = defaultdict(list)
        for msg in extract_messages(self.args.path):
            entry = self._msg_to_entry(msg)
            root = find_project_root(msg.path)
            files[root].append(entry)

        if not files:
            self.print('No entries found')
            return 1
        for root, entries in files.items():
            project = Project(root)
            project.po_root.mkdir(exist_ok=True)
            for lang in self._langs_for(project):
                self.print(lang)
                file_path = project.po_root / f'{lang}.po'

                template_file = polib.POFile()
                template_file.extend(entries)
                if file_path.exists():
                    target_file = polib.pofile(str(file_path))
                    target_file.merge(template_file)
                else:
                    target_file = template_file
                self._set_meta(project, target_file, lang)
                target_file.save(str(file_path))
                self.print(f'  extracted: {len(entries)}')
        return 0

    def _langs_for(self, project: Project) -> Iterator[str]:
        if self.args.lang:
            yield self.args.lang
            return
        found = False
        for po_file in project.po_root.iterdir():
            found = True
            yield po_file.stem
        if not found:
            yield 'en'

    def _msg_to_entry(self, msg: Message) -> polib.POEntry:
        kwargs: dict[str, Any] = {}
        if msg.comment:
            kwargs['comment'] = msg.comment
        if msg.context:
            kwargs['msgctxt'] = msg.context
        if msg.plural is not None:
            kwargs['msgid_plural'] = msg.plural
        flags = []
        if '{' in msg.text:
            flags.append('python-brace-format')
        return polib.POEntry(
            msgid=msg.text,
            msgstr='',
            occurrences=[(msg.file_name, msg.line)],
            flags=flags,
            **kwargs,
        )

    def _set_meta(self, project: Project, po_file: polib.POFile, lang: str) -> None:
        now = datetime.fromisoformat(self.args.now).strftime('%F %H:%M%z')
        plurals = PLURALS.get(lang, GERMANIC)
        meta = po_file.metadata

        meta['Project-Id-Version'] = f'{project.name} {project.version}'
        meta.setdefault('Report-Msgid-Bugs-To', project.bug_tracker)
        meta.setdefault('POT-Creation-Date', now)
        meta['PO-Revision-Date'] = now
        meta.setdefault('Last-Translator', project.author)
        meta.setdefault('Language-Team', project.author)
        meta.setdefault('Language', lang)
        meta.setdefault('MIME-Version', '1.0')
        meta.setdefault('Content-Type', 'text/plain; charset=UTF-8')
        meta.setdefault('Content-Transfer-Encoding', '8bit')
        meta.setdefault('Plural-Forms', str(plurals))
        meta['Generated-By'] = f'l10n {l10n.__version__}'
