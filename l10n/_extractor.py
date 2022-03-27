import json
from pathlib import Path
import sys
import subprocess
from typing import Iterator, NamedTuple, Optional
from mypy.plugin import Plugin, MethodContext
from mypy import types
from tempfile import NamedTemporaryFile

PREFIX = '__L10N__:'


class Message(NamedTuple):
    text: str
    line: int
    column: int
    file_name: str

    @property
    def location(self) -> str:
        return f'{self.file_name}:{self.line}'


def extract_messages(project_path: Path) -> Iterator[Message]:
    config = f'[mypy]\nplugins = {__name__}'
    with NamedTemporaryFile() as tmp_file:
        tmp_file.write(config.encode())
        tmp_file.flush()
        cmd = [
            sys.executable, '-m', 'mypy',
            '--no-incremental',
            '--show-traceback',
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
        message = self._get_message(context)
        if message:
            self._record(
                text=message,
                line=context.context.line,
                column=context.context.column,
                file_name=context.api.path,
            )
        return context.default_return_type

    def _get_message(self, context: MethodContext) -> Optional[str]:
        if not context.arg_types:
            return None
        arg_types = context.arg_types[0]
        if len(arg_types) != 1:
            return None
        arg_type = arg_types[0]
        if not isinstance(arg_type, types.Instance):
            return None
        if arg_type.last_known_value is None:
            return None
        value = arg_type.last_known_value.value
        if not isinstance(value, str):
            return None
        return value

    def _record(self, **data: object) -> None:
        print(PREFIX, json.dumps(data))


def plugin(version: str):
    return LookupPlugin
