from __future__ import annotations

from typing import NamedTuple


class Plural(NamedTuple):
    n: int
    expr: str

    def __str__(self) -> str:
        return f'nplurals={self.n}; plural={self.expr};'


GERMANIC = Plural(2, '(n != 1)')
SINGULAR = Plural(1, '0')
FRENCH = Plural(2, '(n > 1)')
RUSSIAN = Plural(3, '(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)')

# Source:
# http://docs.translatehouse.org/projects/localization-guide/en/latest/l10n/pluralforms.html
# We skipped languages with germanic pluralization because it's default anyway.
PLURALS: dict[str, Plural]
PLURALS = {
    'ach':      FRENCH,
    'ak':       FRENCH,
    'am':       FRENCH,
    'ar':       Plural(6, '(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5)'),
    'arn':      FRENCH,
    'ay':       SINGULAR,
    'be':       RUSSIAN,
    'bo':       SINGULAR,
    'br':       FRENCH,
    'bs':       RUSSIAN,
    'cgg':      SINGULAR,
    'cs':       Plural(3, '(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2'),
    'csb':      Plural(3, '(n==1) ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2'),
    'cy':       Plural(4, '(n==1) ? 0 : (n==2) ? 1 : (n != 8 && n != 11) ? 2 : 3'),
    'dz':       SINGULAR,
    'fa':       FRENCH,
    'fil':      FRENCH,
    'fr':       FRENCH,
    'ga':       Plural(5, 'n==1 ? 0 : n==2 ? 1 : (n>2 && n<7) ? 2 :(n>6 && n<11) ? 3 : 4'),
    'gd':       Plural(4, '(n==1 || n==11) ? 0 : (n==2 || n==12) ? 1 : (n > 2 && n < 20) ? 2 : 3'),
    'gun':      FRENCH,
    'hr':       RUSSIAN,
    'id':       SINGULAR,
    'is':       Plural(2, '(n%10!=1 || n%100==11)'),
    'ja':       SINGULAR,
    'jbo':      SINGULAR,
    'jv':       Plural(2, '(n != 0)'),
    'ka':       SINGULAR,
    'km':       SINGULAR,
    'ko':       SINGULAR,
    'kw':       Plural(4, '(n==1) ? 0 : (n==2) ? 1 : (n == 3) ? 2 : 3'),
    'ln':       FRENCH,
    'lo':       SINGULAR,
    'lt':       Plural(3, '(n%10==1 && n%100!=11 ? 0 : n%10>=2 && (n%100<10 || n%100>=20) ? 1 : 2)'),
    'lv':       Plural(3, '(n%10==1 && n%100!=11 ? 0 : n != 0 ? 1 : 2)'),
    'me':       Plural(3, 'n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2'),
    'mfe':      FRENCH,
    'mg':       FRENCH,
    'mi':       FRENCH,
    'mk':       Plural(2, '(n==1 || n%10==1 ? 0 : 1)'),
    'mnk':      Plural(3, '(n==0 ? 0 : n==1 ? 1 : 2)'),
    'ms':       SINGULAR,
    'mt':       Plural(4, '(n==1 ? 0 : n==0 || ( n%100>1 && n%100<11) ? 1 : (n%100>10 && n%100<20 ) ? 2 : 3)'),
    'my':       SINGULAR,
    'oc':       FRENCH,
    'pl':       Plural(3, '(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'),
    'pt_BR':    FRENCH,
    'ro':       Plural(3, '(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2)'),
    'ru':       RUSSIAN,
    'sah':      SINGULAR,
    'sk':       Plural(3, '(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2'),
    'sl':       Plural(4, '(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)'),
    'sr':       RUSSIAN,
    'su':       SINGULAR,
    'tg':       FRENCH,
    'th':       SINGULAR,
    'ti':       FRENCH,
    'tr':       FRENCH,
    'tt':       SINGULAR,
    'ug':       SINGULAR,
    'uk':       RUSSIAN,
    'uz':       FRENCH,
    'vi':       SINGULAR,
    'wa':       FRENCH,
    'wo':       SINGULAR,
    'zh':       FRENCH,
}
