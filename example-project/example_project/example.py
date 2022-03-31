from argparse import ArgumentParser

from l10n import Locales

locales = Locales()


def say_hello(name: str, lang: str = 'en') -> None:
    loc = locales[lang]
    msg = loc.get('Hello, {user_name}!').format(user_name=name)
    print(msg)


def main():
    parser = ArgumentParser()
    parser.add_argument('--name', default='World')
    parser.add_argument('--lang', default='en')
    args = parser.parse_args()
    say_hello(name=args.name, lang=args.lang)
