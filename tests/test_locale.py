from datetime import date, time
from pathlib import Path

import pytest

from l10n._locale import Locale

SPHINX_MO = Path('/usr/share/locale/ru/LC_MESSAGES/sphinx.mo')


@pytest.mark.skipif(not SPHINX_MO.exists(), reason='no mo file for Sphinx')
def test_read_mo():
    loc = Locale(SPHINX_MO)
    assert loc.language == 'ru'
    msgid = 'Could not import extension %s'
    assert loc.get(msgid) == 'Не могу загрузить модуль расширения %s'


@pytest.mark.parametrize('language, expected', [
    ('ru', '31.12.2021'),
    ('ru_RU', '31.12.2021'),
    ('en', '12/31/2021'),
    ('en_US', '12/31/2021'),
    ('en_UK', '31/12/21'),
    ('hu', '2021-12-31'),
    ('nl', '31-12-21'),
    ('nl_NL', '31-12-21'),
])
def test_format_date(language, expected):
    loc = Locale(language=language)
    given = date(2021, 12, 31)
    assert loc.format_date(given) == expected


@pytest.mark.parametrize('language, expected', [
    ('ru', '23:34:56'),
    ('ru_RU', '23:34:56'),
    ('en', '11:34:56 PM'),
    ('en_US', '11:34:56 PM'),
    ('en_UK', '23:34:56'),
    ('hu', '23:34:56'),
    ('nl', '23:34:56'),
    ('nl_NL', '23:34:56'),
])
def test_format_time(language, expected):
    loc = Locale(language=language)
    given = time(23, 34, 56)
    assert loc.format_time(given) == expected


@pytest.mark.parametrize('language, expected', [
    ('ru', 'ноября'),
    ('ru_RU', 'ноября'),
    ('en', 'November'),
    ('en_US', 'November'),
    ('en_UK', 'November'),
    ('hu', 'november'),
    ('nl', 'november'),
    ('nl_NL', 'november'),
])
def test_format_month(language, expected):
    loc = Locale(language=language)
    assert loc.format_month(11) == expected


@pytest.mark.parametrize('language, expected, expected_abbr', [
    ('ru', 'Понедельник', 'Пн'),
    ('ru_RU', 'Понедельник', 'Пн'),
    ('en', 'Monday', 'Mon'),
    ('en_US', 'Monday', 'Mon'),
    ('en_UK', 'Monday', 'Mon'),
    ('hu', 'hétfő', 'h'),
    ('nl', 'maandag', 'ma'),
    ('nl_NL', 'maandag', 'ma'),
])
def test_format_dow(language, expected, expected_abbr):
    loc = Locale(language=language)
    assert loc.format_dow(1) == expected
    assert loc.format_dow(1, abbreviate=True) == expected_abbr


@pytest.mark.parametrize('n, sunday, expected', [
    (0, 0, 'Sunday'),
    (1, 0, 'Monday'),
    (6, 0, 'Saturday'),

    (1, 1, 'Sunday'),
    (2, 1, 'Monday'),
    (7, 1, 'Saturday'),

    (6, 6, 'Sunday'),
    (0, 6, 'Monday'),
    (5, 6, 'Saturday'),

    (7, 7, 'Sunday'),
    (1, 7, 'Monday'),
    (6, 7, 'Saturday'),
])
def test_format_dow__sunday(n, sunday, expected):
    loc = Locale(language='en')
    assert loc.format_dow(n, sunday=sunday) == expected


@pytest.mark.parametrize('language, expected', [
    ('ru', '₽'),
    ('ru_RU', '₽'),
    ('en', '$'),
    ('en_US', '$'),
    ('en_UK', '£'),
    ('hu', 'Ft'),
    ('nl', 'EUR'),
    ('nl_NL', 'EUR'),
])
def test_currency_symbol(language, expected):
    loc = Locale(language=language)
    assert loc.currency_symbol == expected


@pytest.mark.parametrize('language, expected', [
    ('ru', '-16,00 ₽'),
    ('ru_RU', '-16,00 ₽'),
    ('en', '-$16.00'),
    ('en_US', '-$16.00'),
    ('en_UK', '-£16.00'),
    ('hu', '-16,00 Ft'),
    ('nl', 'EUR 16,00-'),
    ('nl_NL', 'EUR 16,00-'),
])
def test_format_currency(language, expected):
    loc = Locale(language=language)
    assert loc.format_currency(-16) == expected


PATHS = [pytest.param(p, id=p.name) for p in Path('/usr/share/locale').iterdir()]


@pytest.mark.parametrize('root', PATHS)
def test_parse_smoke(root: Path):
    msg_root = (root / 'LC_MESSAGES')
    if not msg_root.exists():
        pytest.skip()
    for path in msg_root.iterdir():
        if path.suffix != '.mo':
            continue
        loc = Locale(path)
        try:
            loc.language
        except (ValueError, IndexError):
            # for some reason, gettext can't parse some plural forms
            pass
