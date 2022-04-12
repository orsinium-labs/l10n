from pathlib import Path
import pytest
import polib
from l10n._cli import main


@pytest.fixture
def translate(project_root: Path):
    def f(*entries):
        po_file = polib.POFile(encoding="UTF-8")
        po_file.metadata['Content-Type'] = 'text/plain; charset=UTF-8'
        po_file.extend(entries)
        po_path = project_root / 'locales' / 'ru.po'
        po_path.parent.mkdir(exist_ok=True)
        po_file.save(str(po_path))
        code = main(['translate', '--path', str(project_root)])
        assert code == 0
        return polib.pofile(str(po_path))
    return f


def test_translate_simple(translate):
    e = polib.POEntry(msgid="Hello world")
    po: polib.POFile = translate(e)
    assert len(po) == 1
    e = po[0]
    assert e.msgid == 'Hello world'
    assert e.flags == ['fuzzy']
    assert e.msgstr == 'Привет, мир'
