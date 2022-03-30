
from types import MappingProxyType
from typing import Mapping, Type

from ._base import Command
from ._compile import Compile
from ._extract import Extract
from ._translate import Translate

COMMANDS: Mapping[str, Type[Command]]
COMMANDS = MappingProxyType(dict(
    compile=Compile,
    extract=Extract,
    translate=Translate,
))
