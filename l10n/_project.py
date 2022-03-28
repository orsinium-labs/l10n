from __future__ import annotations
import getpass
from contextlib import suppress
from functools import cached_property
from typing import Any
from pathlib import Path
from dataclasses import dataclass

try:
    import toml
except ImportError:
    toml = None  # type: ignore[assignment]
try:
    import tomli
except ImportError:
    # https://peps.python.org/pep-0680/
    try:
        import tomllib as tomli  # type: ignore
    except ImportError:
        tomli = None   # type: ignore[assignment]


def find_project_root(start_path: Path) -> Path:
    parents = [start_path] + list(start_path.absolute().parents)
    for dir_path in parents:
        if (dir_path / 'pyproject.toml').is_file():
            return dir_path
    for dir_path in parents:
        if (dir_path / '.git').is_dir():
            return dir_path

    # find the parent directory without __init__.py that contains a directory
    # with __init__.py.
    init_detected = False
    for dir_path in parents:
        if (dir_path / '__init__.py').exists():
            init_detected = True
            continue
        if init_detected:
            return dir_path
        break

    return Path()


@dataclass
class Project:
    root: Path

    @cached_property
    def name(self) -> str:
        with suppress(KeyError):
            return self._meta['tool']['l10n']['name']
        with suppress(KeyError):
            return self._meta['project']['name']
        with suppress(KeyError):
            return self._meta['tool']['flit']['metadata']['module']
        with suppress(KeyError):
            return self._meta['tool']['poetry']['name']
        return self.root.absolute().name

    @cached_property
    def version(self) -> str:
        with suppress(KeyError):
            return self._meta['tool']['l10n']['version']
        with suppress(KeyError):
            return self._meta['project']['version']
        with suppress(KeyError):
            return self._meta['tool']['poetry']['version']
        return '0.0.0'

    @cached_property
    def author_name(self) -> str:
        with suppress(KeyError):
            return self._meta['tool']['l10n']['author_name']
        with suppress(LookupError):
            return self._meta['project']['authors'][0]['name']
        return getpass.getuser()

    @cached_property
    def author_email(self) -> str:
        with suppress(KeyError):
            return self._meta['tool']['l10n']['author_email']
        with suppress(LookupError):
            return self._meta['project']['authors'][0]['email']
        return ""

    @cached_property
    def author(self) -> str:
        if self.author_email:
            return f'{self.author_name} <{self.author_email}>'
        return self.author_name

    @cached_property
    def bug_tracker(self) -> str:
        """URL or e-mail address where bugs in MsgIDs (original text) can be reported.
        """
        return self.author_email

    # PRIVATE

    @cached_property
    def _meta(self) -> dict[str, Any]:
        path = self.root / 'pyproject.toml'
        if not path.exists():
            return {}
        if tomli is not None:
            with path.open('rb') as stream:
                return tomli.load(stream)
        if toml is not None:   # type: ignore[unreachable]
            with path.open('rb', encoding='utf8') as stream:
                return dict(toml.load(stream))
        return {}
