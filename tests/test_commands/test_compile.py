from pathlib import Path
import pytest
import polib
from l10n._cli import main
from l10n import Locale


@pytest.fixture
def compile(project_root: Path):
    def f(*entries):
        po_file = polib.POFile(encoding="UTF-8")
        po_file.metadata['Content-Type'] = 'text/plain; charset=UTF-8'
        po_file.extend(entries)
        po_path = project_root / 'locales' / 'ru.po'
        po_path.parent.mkdir(exist_ok=True)
        po_file.save(str(po_path))
        code = main(['compile', '--path', str(project_root)])
        assert code == 0
        mo_file = project_root / 'project_test' / 'locales' / 'ru.mo'
        assert mo_file.exists()
        return Locale(mo_file)
    return f


def test_compile_simple(compile):
    e = polib.POEntry(msgid="hello world", msgstr="привет мир")
    loc: Locale = compile(e)
    assert loc.get('hello world') == 'привет мир'


def test_include_fuzzy(compile):
    e = polib.POEntry(msgid="hello world", msgstr="привет мир", flags=["fuzzy"])
    loc: Locale = compile(e)
    assert loc.get('hello world') == 'привет мир'
