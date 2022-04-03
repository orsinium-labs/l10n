from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator, NamedTuple

from mypy import types
from mypy.plugin import MethodContext, Plugin
from mypy.types import LiteralValue

PREFIX = '__L10N__:'


class Message(NamedTuple):
    text: str
    line: int
    column: int
    n: int | None
    context: str | None
    comment: str | None
    plural: str | None
    file_name: str

    @property
    def path(self) -> Path:
        return Path(self.file_name)


def extract_messages(project_path: Path) -> Iterator[Message]:
    config = f'[mypy]\nplugins = {__name__}'
    with NamedTemporaryFile() as tmp_file:
        tmp_file.write(config.encode())
        tmp_file.flush()
        cmd = [
            sys.executable, '-m', 'mypy',
            '--no-incremental',
            '--show-traceback',
            '--check-untyped-defs',
            '--config-file', tmp_file.name,
            str(project_path),
        ]
        # result = subprocess.run(cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
    for line in result.stdout.decode().splitlines():
        if not line.startswith(PREFIX):
            continue
        line = line[len(PREFIX):].strip()
        yield Message(**json.loads(line))


class LookupPlugin(Plugin):
    def get_method_hook(self, fullname: str):
        if fullname == 'l10n._locale.Locale.get':
            return self._extractor

    def _extractor(self, context: MethodContext):
        message = self._get_arg('message', context)
        if message:
            self._record(
                text=message,
                n=self._get_arg('n', context),
                context=self._get_arg('context', context),
                comment=self._get_arg('comment', context),
                plural=self._get_arg('plural', context),
                line=context.context.line,
                column=context.context.column,
                file_name=context.api.path,
            )
        return context.default_return_type

    def _get_arg(self, name: str, context: MethodContext) -> LiteralValue | None:
        index = context.callee_arg_names.index(name)
        arg_types = context.arg_types[index]
        if len(arg_types) != 1:
            return None
        arg_type = arg_types[0]
        if not isinstance(arg_type, types.Instance):
            return None
        if arg_type.last_known_value is None:
            return None
        return arg_type.last_known_value.value

    def _record(self, **data: object) -> None:
        print(PREFIX, json.dumps(data))


def plugin(version: str):
    return LookupPlugin
