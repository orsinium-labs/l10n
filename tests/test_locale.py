from pathlib import Path
from l10n._locale import Locale


def test_read_mo():
    path = Path('/usr/share/locale/ru/LC_MESSAGES/sphinx.mo')
    loc = Locale(project='', language='', path=path)
    msgid = 'Could not import extension %s'
    assert loc.get(msgid) == 'Не могу загрузить модуль расширения %s'
