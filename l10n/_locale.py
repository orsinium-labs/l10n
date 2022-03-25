

from pathlib import Path
from typing import Dict, Mapping, Optional, Tuple, Union
from dataclasses import dataclass
from functools import cached_property
import gettext


SingularID = str
PluralID = Tuple[str, int]
MsgID = Union[SingularID, PluralID]
Messages = Dict[MsgID, str]


@dataclass
class Locale:
    project: str
    language: str
    path: Path

    def get(
        self,
        message: str, *,
        context: Optional[str] = None,
        default: Optional[str] = None,
        n: Optional[int] = None,
        vars: Optional[Mapping[str, str]] = None,
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
        if vars is not None:
            translation = translation.format(**vars)
        return translation

    @cached_property
    def _messages(self) -> Messages:
        ext = self.path.suffix
        if ext == '.mo':
            return self._messages_mo
        raise NotImplementedError(f'the locale extension is not supported: {ext}')

    @property
    def _messages_mo(self) -> Messages:
        with self.path.open('rb') as stream:
            tr = gettext.GNUTranslations(stream)    # type: ignore[arg-type]
        self._plural_id = tr.plural                 # type: ignore
        return tr._catalog                          # type: ignore[attr-defined]

    def _plural_id(self, n: int) -> int:
        return int(n != 1)
