from pathlib import Path
import sys
from argparse import ArgumentParser
from typing import List, NoReturn, Optional, TextIO, Type
from ._commands import COMMANDS, Command


def main(argv: List[str], stream: TextIO) -> int:
    exe = Path(sys.executable).name
    parser = ArgumentParser(f"{exe} -m l10n")
    subparsers = parser.add_subparsers()
    parser.set_defaults(cmd=None)

    cmd_class: Optional[Type[Command]]
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
