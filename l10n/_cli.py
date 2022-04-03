from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import NoReturn, TextIO

from ._commands import COMMANDS, Command


def main(argv: list[str], stream: TextIO = sys.stdout) -> int:
    exe = Path(sys.executable).name
    parser = ArgumentParser(f'{exe} -m l10n')
    subparsers = parser.add_subparsers()
    parser.set_defaults(cmd=None)

    cmd_class: type[Command] | None
    for name, cmd_class in COMMANDS.items():
        subparser = subparsers.add_parser(name=name, help=cmd_class.__doc__)
        subparser.set_defaults(cmd=cmd_class)
        cmd_class.init_parser(subparser)

    args = parser.parse_args(argv)
    cmd_class = args.cmd
    if cmd_class is None:
        parser.print_help()
        return 1
    cmd = cmd_class(args=args, stream=stream)
    return cmd.run()


def entrypoint() -> NoReturn:
    sys.exit(main(argv=sys.argv[1:], stream=sys.stdout))
