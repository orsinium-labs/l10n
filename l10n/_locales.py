

import os
from pathlib import Path
import re
from typing import FrozenSet, Iterator, Optional, Pattern, Tuple
from dataclasses import dataclass
from functools import cached_property
from ._locale import Locale
import fnmatch


DEFAULT_CATALOG = Path('/', 'usr', 'share', 'locale')


@dataclass
class Locales:
    project: str = ''
    catalog: Path = DEFAULT_CATALOG
    format: Optional[str] = None
    extension: str = '.mo'

    def get(self, language: str) -> Optional[Locale]:
        """Find locale file for the given language.
        """
        path = self._path_to(language)
        if not path.exists():
            return None
        return Locale(project=self.project, language=language, path=path)

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
        for path in self.catalog.glob(self._pattern):
            language = self._extract_language(path)
            locale = Locale(project=self.project, language=language, path=path)
            locales.append(locale)
        return tuple(locales)

    # PRIVATE

    def _extract_language(self, path: Path) -> str:
        path = path.relative_to(self.catalog)
        text = str(path).replace(os.path.sep, '/')
        match = self._rex.fullmatch(text)
        assert match, "cannot extract language from path"
        return match.group(1)

    def _path_to(self, language: str) -> Path:
        parts = self._pattern.replace('*', language).split('/')
        return self.catalog.joinpath(*parts)

    @cached_property
    def _rex(self) -> Pattern:
        return re.compile(fnmatch.translate(self._pattern))

    @cached_property
    def _pattern(self) -> str:
        if not self.catalog.exists():
            raise FileNotFoundError(f'No such directory: {self.catalog}')
        if self.format is not None:
            return self.format.replace('{language}', '*')
        for format in self._default_formats:
            pattern = format.format(
                language='*',
                project=self.project,
                ext=self.extension,
            )
            for _ in self.catalog.glob(pattern):
                return pattern
        raise FileNotFoundError('No locales found. Try specifying `Locale.format`.')

    @property
    def _default_formats(self) -> Iterator[str]:
        if self.project:
            yield '{language}/LC_MESSAGES/{project}{ext}'
            yield '{project}/{language}{ext}'
            yield '{language}/{project}{ext}'
            yield '{project}-{language}{ext}'
        else:
            yield '{language}{ext}'

    # MAGIC

    def __getattr__(self, language: str) -> Locale:
        locale = self.get(language)
        if locale is None:
            raise KeyError(language)
        return locale

    def __iter__(self) -> Iterator[Locale]:
        yield from self.locales
