from __future__ import annotations
import datetime
import threading
import gettext
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Tuple, Union
import locale

SingularID = str
PluralID = Tuple[str, int]
MsgID = Union[SingularID, PluralID]
locale_lock = threading.Lock()


@dataclass
class Locale:
    path: Path

    def get(
        self,
        message: str, *,
        context: str | None = None,
        default: str | None = None,
        n: int | None = None,
        comment: str = '',
    ) -> str:
        # lookup the message
        msgid_str = message
        if context is not None:
            msgid_str = f'{context}\x04{msgid_str}'
        msgid: MsgID = msgid_str
        if n is not None:
            msgid = (msgid_str, self._plural_id(n))
        translation = self._messages.get(msgid)

        # postprocess the message
        if translation is None:
            translation = default or message
        return translation

    @property
    def language(self) -> str:
        return self._headers.get('language', '')

    def format_date(self, date: datetime.date) -> str:
        format = self._get_locale_info(locale.D_FMT)
        return date.strftime(format)

    def format_time(self, time: datetime.time) -> str:
        format = self._get_locale_info(locale.T_FMT)
        return time.strftime(format)

    def format_datetime(self, dt: datetime.datetime) -> str:
        format = self._get_locale_info(locale.D_T_FMT)
        return dt.strftime(format)

    def format_month(self, n: int, *, abbreviate: bool = False) -> str:
        prefix = 'AB' if abbreviate else ''
        info_key = getattr(locale, f'{prefix}MON_{n}')
        return self._get_locale_info(info_key)

    def format_dow(self, n: int, *, abbreviate: bool = False, sunday: int = 0) -> str:
        if sunday not in {0, 1, 6, 7}:
            raise TypeError('invalid value for sunday')
        n = n % 7
        if sunday in (0, 7):
            n += 1
            if n == 8:
                n = 1
        prefix = 'AB' if abbreviate else ''
        info_key = getattr(locale, f'{prefix}DAY_{n}')
        return self._get_locale_info(info_key)

    # PRIVATE

    def _get_locale_info(self, info_key: int) -> str:
        with locale_lock:
            old_lang, old_enc = locale.getlocale()
            locale.setlocale(locale.LC_ALL, locale.normalize(self.language))
            try:
                return locale.nl_langinfo(info_key)
            finally:
                locale.setlocale(locale.LC_ALL, f'{old_lang}.{old_enc}')

    @cached_property
    def _messages(self) -> dict[MsgID, str]:
        with self.path.open('rb') as stream:
            tr = gettext.GNUTranslations(stream)    # type: ignore[arg-type]
        self._plural_id = tr.plural                 # type: ignore
        self._headers = tr._info                    # type: ignore[attr-defined]
        return tr._catalog                          # type: ignore[attr-defined]

    @cached_property
    def _headers(self) -> dict[str, str]:
        self._messages
        return self.__dict__['_headers']

    def _plural_id(self, n: int) -> int:
        return int(n != 1)
