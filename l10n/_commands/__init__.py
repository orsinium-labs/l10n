
from types import MappingProxyType
from typing import Mapping, Type
from ._compile import Compile
from ._generate import Generate
from ._base import Command

COMMANDS: Mapping[str, Type[Command]]
COMMANDS = MappingProxyType(dict(
    compile=Compile,
    generate=Generate,
))
