
from types import MappingProxyType
from typing import Mapping, Type

from ._base import Command
from ._compile import Compile
from ._generate import Generate

COMMANDS: Mapping[str, Type[Command]]
COMMANDS = MappingProxyType(dict(
    compile=Compile,
    generate=Generate,
))
