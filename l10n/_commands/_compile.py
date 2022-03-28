from argparse import ArgumentParser
from pathlib import Path
import polib
from ._base import Command
from .._project import Project, find_project_root


class Compile(Command):
    """Generate `.mo` files out of `.po` files.
    """
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--path', type=Path, default=Path(),
            help='the base directory from where to start project root lookup',
        )

    def run(self) -> int:
        project_root = find_project_root(self.args.path)
        project = Project(project_root)
        project.mo_root.mkdir(exist_ok=True)
        for po_path in project.po_root.iterdir():
            print(po_path.stem)
            po_file = polib.pofile(str(po_path))
            mo_path = project.mo_root / f'{po_path.stem}.mo'
            po_file.save_as_mofile(str(mo_path))
        return 0
