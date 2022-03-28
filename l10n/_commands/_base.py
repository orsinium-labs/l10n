

import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import TextIO


@dataclass
class Command:
    args: Namespace
    stream: TextIO = sys.stdout

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        return None

    def run(self) -> int:
        return 0

    def print(self, text: str):
        print(text, file=self.stream)
