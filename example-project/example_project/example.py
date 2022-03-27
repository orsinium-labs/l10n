from l10n import Locales

locales = Locales()


def say_hello(user_name: str, lang: str = 'en') -> None:
    loc = locales[lang]
    msg = loc.get("Hello, {user_name}!").format(user_name=user_name)
    print(msg)
