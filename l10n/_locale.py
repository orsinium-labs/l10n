from __future__ import annotations
from contextlib import contextmanager
import datetime
from decimal import Decimal
import threading
import gettext
from functools import cached_property
from pathlib import Path
from typing import Tuple, Union
import locale

SingularID = str
PluralID = Tuple[str, int]
MsgID = Union[SingularID, PluralID]
locale_lock = threading.Lock()
SYSTEM_LOCALES = Path('/usr/share/locale')


class Locale:
    def __init__(self, path: Path | None = None, *, language: str | None = None) -> None:
        self.path = path
        self._lang = language

    def reset_cache(self) -> None:
        """Reset all the cached values for the locale object.

        Use it if you need to reload the mo file.
        """
        path = self.path
        lang = self._lang
        vars(self).clear()
        self.path = path
        self._lang = lang

    def get(
        self,
        message: str, *,
        context: str | None = None,
        plural: str | None = None,
        n: int | None = None,
        comment: str = '',
    ) -> str:
        """Get translation for the message from the catalog (mo file).

        Args:
            message: the message to translate.
                If no translation found, the message itself will be used.
                Represented as `msgid` in PO files.
            context: kind of namespace for translations, used to distinguish
                two messages that may have a different translation depending
                on the context they are used in. Represented as `msgctxt` in PO files.
            plural: the default value if `n > 1` and no translation found.
                It also indicates for translator that the message should have
                plural translations. Represented as `msgid_plural` in PO files.
            n: the number used to pick a plural form for the translation.
            comment: not used in runtime but included in PO files.
                Use it to provide additional information for translators.
        """
        msgid_str = message
        if context is not None:
            msgid_str = f'{context}\x04{msgid_str}'
        msgid: MsgID = msgid_str
        if n is not None:
            msgid = (msgid_str, self._plural_id(n))
        translation = self._messages.get(msgid)

        if translation is not None:
            return translation
        if n is not None and n != 1:
            return plural or message
        return message

    @property
    def language(self) -> str:
        """The language of the Locale.
        """
        if self._lang:
            return self._lang
        return self._headers.get('language', '')

    def format_date(self, date: datetime.date) -> str:
        """Format date.

        You need the locale do be compiled in your OS.
        """
        format = self._get_locale_info(locale.D_FMT)
        return date.strftime(format)

    def format_time(self, time: datetime.time) -> str:
        """Format time.

        You need the locale do be compiled in your OS.
        """
        format = self._get_locale_info(locale.T_FMT)
        return time.strftime(format)

    def format_datetime(self, dt: datetime.datetime) -> str:
        """Format date and time.

        You need the locale do be compiled in your OS.
        """
        format = self._get_locale_info(locale.D_T_FMT)
        return dt.strftime(format)

    def format_month(self, n: int, *, abbreviate: bool = False) -> str:
        """Format the month number into its name.

        You need the locale do be compiled in your OS.
        """
        prefix = 'AB' if abbreviate else ''
        info_key = getattr(locale, f'{prefix}MON_{n}')
        return self._get_locale_info(info_key)

    def format_dow(self, n: int, *, abbreviate: bool = False, sunday: int = 0) -> str:
        """Format the day of week.

        You need the locale do be compiled in your OS.

        Args:
            abbreviate: Use the short version of the DoW.
            sunday: Depending on your country and if you count from 0 or 1,
                different numbers correspond to a different day of week.
                The sunday argument allows you to specify what number is Sunday for you.
                By default, it is `0` assuming that the first DoW is Sunday
                and you count days from 0 to 6.
        """
        if sunday not in {0, 1, 6, 7}:
            raise TypeError('invalid value for sunday')
        n = (n - 1) % 7 + 1
        if sunday in (0, 7):
            n += 1
            if n == 8:
                n = 1
        elif sunday == 6:
            n = (n - 6) % 7 + 1
        prefix = 'AB' if abbreviate else ''
        info_key = getattr(locale, f'{prefix}DAY_{n}')
        return self._get_locale_info(info_key)

    @cached_property
    def currency_symbol(self) -> str:
        """The symbol used to denote the currency.

        You need the locale do be compiled in your OS.
        """
        return self._get_locale_info(locale.CRNCYSTR)[1:]

    @cached_property
    def decimal_dot(self) -> str:
        """The symbol used to separate whole and fractional parts in decimal numbers.

        Also known as decimal dot, decimal comma, radix character.

        You need the locale do be compiled in your OS.
        """
        return self._get_locale_info(locale.RADIXCHAR)

    @cached_property
    def thousands_separator(self) -> str:
        """The symbol used to separate groups of digits in big numbers.

        In most of the languages, it separates groups of three digits.
        In some locales, though, digits are grouped by 4.

        https://en.wikipedia.org/wiki/Decimal_separator

        You need the locale do be compiled in your OS.
        """
        return self._get_locale_info(locale.THOUSEP)

    def format_currency(
        self,
        val: int | float | Decimal, *,
        symbol: bool = True,
        international: bool = False,
        grouping: bool = False,
    ) -> str:
        """Format a price in the locale currency.

        1. The locale currency symbol will be added.
        2. The currency symbol will be placed in the right position.
        3. The minus for negative numbers will be placed in the right position.
        4. The locale decimal separator will be used.

        Args:
            symbol: include the currency symbol.
            international: use international currency symbol.
            grouping: add thousands separator.
        """
        with self._context():
            return locale.currency(
                val,
                symbol=symbol,
                grouping=grouping,
                international=international,
            )

    def format_float(
        self,
        n: int | float | Decimal, *,
        grouping: bool = False,
        monetary: bool = False,
        precision: int | None = None,
        strip_zeros: bool | None = None,
        exp: bool = False,
    ) -> str:
        """Format float or Decimal with the correct decimal dot.

        Args:
            grouping: add thousands separator.
            monetary: use monetary thousands separator which may be different
                from a regular one for some locales.
            precision: if specified, include exactly so many digits in the decimal part.
            strip_zeros: whatever to remove trailing zeros from the end.
                If not specified, will be set to `True` only if precision
                is not specified.
            exp: if True, represent large numbers in scientific exponent notation.
        """
        fmt_suffix = 'g' if exp else 'f'
        fmt = f'%.{precision}{fmt_suffix}' if precision is not None else f'%{fmt_suffix}'
        with self._context():
            result = locale.format_string(fmt, n, grouping=grouping, monetary=monetary)
        if strip_zeros is None:
            strip_zeros = precision is None
        if strip_zeros:
            result = result.rstrip('0')
        return result

    format_decimal = format_float

    def format_int(self, n: int, grouping: bool = True) -> str:
        """Format an integer with grouping (thousands separator).

        If you need to show an integer without grouping, you don't need l10n.
        All languages display whole numbers in arabic numerals in the same way.

        https://en.wikipedia.org/wiki/Arabic_numerals
        https://en.wikipedia.org/wiki/Decimal_separator
        """
        if not grouping:
            return str(n)
        with self._context():
            return f'{n:n}'

    def parse_float(self, s: str) -> float:
        """Convert string generated by `Locale.format_float` back into float.
        """
        with self._context():
            return locale.atof(s)

    def parse_int(self, s: str) -> int:
        """Convert string generated by `Locale.format_int` back into int.
        """
        with self._context():
            return locale.atoi(s)

    def translate_country(self, country_name: str) -> str:
        """Translate country name from English to the given language.

        Follows ISO 3166-1. Requires `iso-codes` package to be installed.
        https://en.wikipedia.org/wiki/ISO_3166-1
        """
        if not self._iso_3166_1:
            return country_name
        return self._iso_3166_1.get(country_name)

    def translate_currency(self, currency_name: str) -> str:
        """Translate currency name from English to the given language.

        Follows ISO 4217. Requires `iso-codes` package to be installed.
        https://en.wikipedia.org/wiki/ISO_4217
        """
        if not self._iso_4217:
            return currency_name
        return self._iso_4217.get(currency_name)

    def translate_language(self, language_name: str) -> str:
        """Translate language name from English to the given language.

        Follows ISO 639-2 and ISO 639-3. Requires `iso-codes` package to be installed.
        https://en.wikipedia.org/wiki/ISO_639-2
        https://en.wikipedia.org/wiki/ISO_639-3
        """
        if self._iso_639_2:
            transl = self._iso_639_2.get(language_name)
            if transl != language_name:
                return transl
        if self._iso_639_3:
            transl = self._iso_639_3.get(language_name)
            if transl != language_name:
                return transl
        return language_name

    # PRIVATE

    @cached_property
    def _iso_3166_1(self) -> Locale | None:
        return self._read_system_messages('iso_3166-1.mo')

    @cached_property
    def _iso_4217(self) -> Locale | None:
        return self._read_system_messages('iso_4217.mo')

    @cached_property
    def _iso_639_2(self) -> Locale | None:
        return self._read_system_messages('iso_639-2.mo')

    @cached_property
    def _iso_639_3(self) -> Locale | None:
        return self._read_system_messages('iso_639-3.mo')

    def _read_system_messages(self, name: str) -> Locale | None:
        long_lang = locale.normalize(self.language).split('.')[0]
        short_lang = long_lang.split('_')[0].split('-')[0]
        for lang in (self.language, long_lang, short_lang):
            path = SYSTEM_LOCALES / lang / 'LC_MESSAGES' / name
            if path.exists():
                return Locale(path, language=lang)
        return None

    def _get_locale_info(self, info_key: int) -> str:
        with self._context():
            return locale.nl_langinfo(info_key)

    @contextmanager
    def _context(self):
        with locale_lock:
            old_lang, old_enc = locale.getlocale()
            locale.setlocale(locale.LC_ALL, locale.normalize(self.language))
            try:
                yield
            finally:
                locale.setlocale(locale.LC_ALL, (old_lang, old_enc))

    @cached_property
    def _messages(self) -> dict[MsgID, str]:
        if self.path is None:
            raise RuntimeError('path to mo file is not specified for the Locale')
        with self.path.open('rb') as stream:
            tr = gettext.GNUTranslations(stream)    # type: ignore[arg-type]
        self._plural_id = tr.plural                 # type: ignore
        self._headers = tr._info                    # type: ignore[attr-defined]
        return tr._catalog                          # type: ignore[attr-defined]

    @cached_property
    def _headers(self) -> dict[str, str]:
        self._messages
        return vars(self)['_headers']

    def _plural_id(self, n: int) -> int:
        return int(n != 1)

    # MAGIC METHODS

    def __repr__(self) -> str:
        return f'{type(self).__name__}(path={self.path}, language={self._lang})'

    def __eq__(self, other):
        if not isinstance(other, Locale):
            return NotImplemented
        if self.path:
            return self.path == other.path
        return self._lang == other._lang
