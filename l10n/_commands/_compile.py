from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

import polib

from .._project import Project, find_project_root
from ._base import Command


class Compile(Command):
    """Generate `.mo` files out of `.po` files.
    """
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--path', type=Path, default=Path(),
            help='the base directory from where to start project root lookup',
        )
        parser.add_argument(
            '--no-fuzzy', action='store_true',
            help='do not include fuzzy translations',
        )

    def run(self) -> int:
        project_root = find_project_root(self.args.path)
        project = Project(project_root)
        project.mo_root.mkdir(exist_ok=True)
        code = 0
        for po_path in project.po_root.iterdir():
            if po_path.suffix != '.po':
                continue
            self.print(po_path.stem)
            po_file = polib.pofile(str(po_path))

            # remove `fuzzy` flag from all entries unless `--no-fuzzy` is set.
            if not self.args.no_fuzzy:
                for entry in po_file:
                    if entry.fuzzy:
                        entry.flags.remove('fuzzy')

            # check if there is at least one translated entry
            translated = sum(e.translated() for e in po_file)
            if not translated:
                self.print('  no translated strings found')
                code += 1
                continue
            self.print(f'  included: {translated}')

            mo_path = project.mo_root / f'{po_path.stem}.mo'
            po_file.save_as_mofile(str(mo_path))
        return code
