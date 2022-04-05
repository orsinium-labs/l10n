import os
from pathlib import Path

import pytest
from l10n import Locales


def test_system_language():
    default = os.environ.get('LC_ALL')
    os.environ['LC_ALL'] = 'nl_NL.UTF-8'
    try:
        loc = Locales()
        assert loc.system_language == 'nl_NL'
    finally:
        if default is not None:
            os.environ['LC_ALL'] = default


def test_get_locale(tmp_path: Path):
    ru_path = tmp_path / 'ru.mo'
    ru_path.write_text('')
    locales = Locales(path=tmp_path)
    assert locales['ru'].path == ru_path
    assert locales['ru_RU'].path == ru_path
    assert locales.get('ru') is not None
    assert locales.get('en') is None
    with pytest.raises(KeyError):
        locales['en']
