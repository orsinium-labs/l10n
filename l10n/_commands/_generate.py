from pathlib import Path
import polib
from ._base import Command
from .._extractor import extract_messages, Message


class Generate(Command):
    """Generate a `.po` file for a language.
    """

    def run(self) -> int:
        path = Path('.')
        file = polib.POFile()
        for msg in extract_messages(path):
            file.append(self._msg_to_entry(msg))
        return 0

    def _msg_to_entry(self, msg: Message) -> polib.POEntry:
        return polib.POEntry(
            msgid=msg.text,
            msgstr='',
            comment=f'{msg.location}',
        )
