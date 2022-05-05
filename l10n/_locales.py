from __future__ import annotations

import fnmatch
import inspect
import locale
import re
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Iterator

from ._locale import Locale


class Locales:
    """Class allowing you to work with compiled (.mo) files collection.

    Args:
        path: where compiled locales are located.
        format: file name template for compiled locales.
    """
    _path: Path | None
    format: str

    def __init__(
        self, *,
        path: Path | None = None,
        format: str = '{language}.mo',
    ) -> None:
        self._path = path
        self.format = format

    def get(self, language: str) -> Locale | None:
        """Find locale for the given language.
        """
        path = self._path_to(language)
        if path.exists():
            return Locale(path, language=language)
        short_lang = language.split('_')[0].split('-')[0]
        path = self._path_to(short_lang)
        if path.exists():
            return Locale(path, language=language)
        return None

    @lru_cache(maxsize=16)
    def get_cached(self, language: str) -> Locale | None:
        """The same as get but caches the returned Locale.
        """
        return self.get(language)

    @cached_property
    def path(self) -> Path:
        if self._path is not None:
            return self._path
        return self._find_catalog()

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
        return locale.getdefaultlocale()[0]

    def reset_cache(self) -> None:
        path = self._path
        format = self.format
        vars(self).clear()
        self._path = path
        self.format = format

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
        for frame in inspect.stack():
            if frame.filename == __file__:
                continue
            file_path = Path(frame.filename)
            if file_path.name == 'functools.py':
                continue
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
