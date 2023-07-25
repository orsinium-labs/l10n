"""A library and CLI for translating Python applications and libraries.
"""
from ._locale import Locale
from ._locales import Locales
from ._cli import entrypoint


__version__ = '0.1.4'
__all__ = ['Locales', 'Locale', 'entrypoint']
