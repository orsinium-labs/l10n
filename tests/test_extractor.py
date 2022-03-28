from pathlib import Path

from l10n._extractor import extract_messages

ROOT = Path(__file__).parent.parent


def test_extract_messages__example():
    path = ROOT / 'example-project'
    messages = list(extract_messages(path))
    assert [m.text for m in messages] == [
        'Hello, {user_name}!',
    ]
