from __future__ import annotations
import fnmatch
import inspect
import os
import re
from functools import cached_property
from pathlib import Path
from typing import Iterator

from ._locale import Locale


class Locales:
    """Class allowing you to work with compiled (.mo) files collection.

    Args:
        path: where compiled locales are located.
        format: file name template for compiled locales.
    """
    path: Path
    format: str

    def __init__(
        self, *,
        path: Path | None = None,
        format: str = '{language}.mo',
    ) -> None:
        if path is None:
            path = self._find_catalog()
        self.path = path
        self.format = format

    def get(self, language: str) -> Locale | None:
        """Find locale for the given language.
        """
        path = self._path_to(language)
        if path.exists():
            return Locale(path)
        language = language.split('_')[0]
        path = self._path_to(language)
        if path.exists():
            return Locale(path)
        return None

    @cached_property
    def languages(self) -> frozenset[str]:
        """List all languages for which a locale is available in the catalog.
        """
        return frozenset(locale.language for locale in self.locales)

    @cached_property
    def locales(self) -> tuple[Locale, ...]:
        """List all locales available in the catalog.
        """
        locales = []
        for path in self.path.glob(self._pattern):
            locales.append(Locale(path))
        return tuple(locales)

    @cached_property
    def system_locale(self) -> Locale | None:
        """The Locale for the default system language.
        """
        if self.system_language is None:
            return None
        return self.get(self.system_language)

    @cached_property
    def system_language(self) -> str | None:
        """The current system language detected from env vars.
        """
        for var_name in ('LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'LANG'):
            value = os.environ.get(var_name, '')
            value = value.split(':')[0].split('.')[0]
            if value:
                return value
        return ''

    # PRIVATE

    def _path_to(self, language: str) -> Path:
        parts = self.format.format(language=language).split('/')
        return self.path.joinpath(*parts)

    @cached_property
    def _rex(self) -> re.Pattern:
        return re.compile(fnmatch.translate(self._pattern))

    @cached_property
    def _pattern(self) -> str:
        return self.format.replace('{language}', '*')

    @staticmethod
    def _find_catalog() -> Path:
        for frame in inspect.stack()[2:]:
            file_path = Path(frame.filename)
            for dir_path in file_path.parents:
                catalog_path = dir_path / 'locales'
                if dir_path.exists():
                    return catalog_path
        raise FileNotFoundError('cannot find catalog')

    # MAGIC

    def __getitem__(self, language: str) -> Locale:
        """The same as Locales.get but raises KeyError if no Locale found.
        """
        locale = self.get(language)
        if locale is None:
            raise KeyError(language)
        return locale

    def __iter__(self) -> Iterator[Locale]:
        """Iterate thorugh all compiled locales.
        """
        yield from self.locales
