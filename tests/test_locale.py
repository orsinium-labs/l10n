from pathlib import Path

import pytest

from l10n._locale import Locale


def test_read_mo():
    path = Path('/usr/share/locale/ru/LC_MESSAGES/sphinx.mo')
    loc = Locale(path)
    assert loc.language == 'ru'
    msgid = 'Could not import extension %s'
    assert loc.get(msgid) == 'Не могу загрузить модуль расширения %s'


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
