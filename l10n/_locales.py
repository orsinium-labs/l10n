

import fnmatch
import inspect
import re
from functools import cached_property
from pathlib import Path
from typing import FrozenSet, Iterator, Optional, Pattern, Tuple

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
        path: Optional[Path] = None,
        format: str = '{language}.mo',
    ) -> None:
        if path is None:
            path = self._find_catalog()
        self.path = path
        self.format = format

    def get(self, language: str) -> Optional[Locale]:
        """Find locale file for the given language.
        """
        path = self._path_to(language)
        if not path.exists():
            return None
        return Locale(path)

    @cached_property
    def languages(self) -> FrozenSet[str]:
        """List all languages for which a locale is available in the catalog.
        """
        return frozenset(locale.language for locale in self.locales)

    @cached_property
    def locales(self) -> Tuple[Locale, ...]:
        """List all locales available in the catalog.
        """
        locales = []
        for path in self.path.glob(self._pattern):
            locales.append(Locale(path))
        return tuple(locales)

    # PRIVATE

    def _path_to(self, language: str) -> Path:
        parts = self.format.format(language=language).split('/')
        return self.path.joinpath(*parts)

    @cached_property
    def _rex(self) -> Pattern:
        return re.compile(fnmatch.translate(self._pattern))

    @cached_property
    def _pattern(self) -> str:
        return self.format.replace('{language}', '*')

    @staticmethod
    def _find_catalog():
        for frame in inspect.stack()[2:]:
            file_path = Path(frame.filename)
            for dir_path in file_path.parents:
                catalog_path = dir_path / 'locales'
                if dir_path.exists():
                    return catalog_path
        raise FileNotFoundError('cannot find catalog')

    # MAGIC

    def __getitem__(self, language: str) -> Locale:
        locale = self.get(language)
        if locale is None:
            raise KeyError(language)
        return locale

    def __iter__(self) -> Iterator[Locale]:
        yield from self.locales
