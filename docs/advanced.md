# Advanced usage

## If translation is missed

If there is no translation for the message in the mo file, `Locale.get` will return the message itself. This is how `gettext` and all its ports work. The motivation is that translations aren't so important as the actual business logic of the application, so it's better to show one message on English rather than fail. Either way, such situations should be avoided, and there are a few tips on how:

+ Run `l10n extract` each time you touch anything related to translated strings.
+ Run `l10n compile` each time you update the translation files.
+ Add commands above into your [pre-commit hooks](https://pre-commit.com/) and on CI.
+ If your target audience doesn't know a word of English, run `l10n translate` to temporarily populate new messages by bad translations.

## Format strings

Use `str.format` to format strings:

```python
loc = locales[lang]
msg = loc.get('Hello, {user_name}!').format(user_name=user.name)
```

Such entries will have `python-brace-format`, so the other tools you may use should correctly detect it as a format tool. In particular, `l10n translate` will not translate the placeholders. So, the message above will be correctly translated on Russian as "Привет, {user_name}!" instead of "Привет, {имя_пользователя}!".

Do not use f-strings. Otherwise, the message will be formatted before it gets translated, so l10n will not be able to find the correct translation for it.

## Plural forms

First you should understand that many languages have multiple plural forms (and some have only one form) meaing that different words should be used depending on the number. For example, in English you have 2 forms:

1. 1 message.
1. 2 messages, 3 messages...

And the same in Russian has 3 forms:

1. 1 сообщение, 21 сообщение...
1. 2 сообщения, 3 сообщения...
1. 5 сообщений, 6 сообщений, 11 сообщений, 12 сообщений...

And Arabic even has 6 forms! The good news is that if you use l10n, things aren't so complex for you. All you need to do is to pass the argument `n` into `Locale.get` which will be used to pick the right plural form for thetranslation:

```python
n_msgs = 13
locale = Locales()['ru']
msg = locale.get('{n} message(s)', n=n_msgs).format(n=n_msgs)
```

Additionally, you can specify the argument `plural` which is the default message to be used if no translation is found and `n!=1` (we assume that you use English or another germanic language for your messages):

```python
msg = locale.get('{n} message', n=n_msgs, plural='{n} messages').format(n=n_msgs)
```

The best thing you can do, though, is to avoid plurals (or even translations) altogether. For example:

+ Use an icon of an envelope (✉️) instead of the word "message".
+ Write it as "messages: 1", so you only need to translate the word "messages".
+ At last, don't use a number, just say "You have a new message".

When you run `l10n extract`, the generated po file will contain a special header `Plural-Forms` which indicates how many plural forms the language has in total and contains a C-expression used to pick the right form based on the number. l10n will fill the field with the correct expression for all languages it knows (or just assume the germanic form). Also, for each entry where you specified the `plural` argument, it will use it as `msgid_plural` which is an indication for the translator that the message is supposed to have a plural form.

## Fuzzy and obsolete entries

Th po file format allows to add different flags to entries. One of such flags is "fuzzy" which means that the entry might have a wrong translation and so it needs to be checked by the translator. When you run `l10n translate`, all auto-translated entries will be marked as fuzzy.

When you run `l10n compile`, it will include fuzzy translations in the mo file, which is a different behavior from all other po to mo compilation tools. We think that imperfect translation is better than no translation at all. Also, that would be confusing for user if they translate a message using `l10n translate`, compile it but still don't see the translation in their app. If you want to be strict and don't want to have fuzzy entries in your app, add `--no-fuzzy` flag when running `l10n compile`.

Another interesting flag is "obsolete". When you run `l10n extract`, it will mark as "obsolete" all translations that have a translation but aren't in the source code anymore. Usually, you can just safely remove these entries. The tool doesn't do it for you because often the message is still there, you just change its ID. In such cases, you can take the obsolete translation, add it to the new ID, and mark it as "fuzzy", so the translator later can adjust the translation according to what you changed in the message.

## Including additional strings

If you need to include into your translation files some strings that aren't explicitly used in the code, you can, well, use them in the code. If you want to avoid evaluating them in runtime, use the fact that `l10n extract` works on top of a static type checker:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from l10n import Locales
    loc = Locales()['en']
    loc.get('hello world')
    loc.get('oh hi mark')
```

If you already have the strings explicitly listed somewhere and you don't want to duplicate them in the Python code, consider extracting them using [xgettext](https://www.gnu.org/software/gettext/manual/html_node/xgettext-Invocation.html) and then merging into the po files with [msgcat](https://www.gnu.org/software/gettext/manual/html_node/msgcat-Invocation.html).

## Localizing dates and numbers

To use these functions, you have to install all needed locales in your OS. On Linux, you can list all installed locales using `locale -a` and install a new one using `sudo locale-gen ru_RU.UTF-8The same should also work for OS X.

The `Locale` object provides the following lcoalization functions:

+ `format_date`
+ `format_time`
+ `format_datetime`
+ `format_month`
+ `format_dow`
+ `format_currency`
+ `format_float`
+ `format_decimal`
+ `format_int`
+ `parse_float`
+ `parse_int`

## Translating languages, countries, and currencies

Locale object also knows how to discover and read some predefined translations installed in your system. On Linux, run `dpkg -s iso-codes` to see if they are installed and if not, install them using `sudo apt install iso-codes`.

The `Locale` object provides the following translation functions:

+ `translate_country`
+ `translate_currency`
+ `translate_language`

## Translating HTML and JS

If you need to translate messages outside of Python code, you'll need other tools in addition to l10n. The main focus of l10n is only Python: "Do one thing and do it well". There are some of our favorites for JS:

+ [i18next](https://github.com/i18next/i18next) for translating messages.
+ [Format.js](https://formatjs.io/) for numbers, date, and time.
+ [Angular](https://angular.io/guide/i18n-overview) has some solutions out-of-the-box.

Often, however, it can be a good idea to keep all translations in one place, inside of your Python code. For example:

+ If you use a template language like [Jinja2](https://palletsprojects.com/p/jinja/) or [Genshi](https://genshi.edgewall.org/), you can extract translations on the Python side and pass inside the template already translated strings.
+ If you have some dynamic content to be rendered on the client side, you can have a thin client and provide for JS code an API that will return already translated messages.

## Performance and hot reload

If you have a long-running app that should not be restarted when you update translations, you should know how l10n caches things:

+ We use [functools.cached_property](https://docs.python.org/3/library/functools.html#functools.cached_property) for caching heavy things. That means, when you request them for the first time, they get cached forever.
+ `l10n.Locales` caches the path to locales directory and which languages are available when you request the first locale.
+ `l10n.Locale` caches all the messages when you request the first one.
+ You can reset the cache by calling the `reset_cache` method of `l10n.Locale` or `l10n.Locales`.
+ Cache is the local to the instance. So, if you create a new instance of `l10n.Locales` (or get a new `l10n.Locale` from the catalog), it doesn't have the old cache.

For example, in getting started tutorial we have `locales = Locales()` at the module-level and `loc = locales[lang]` inside the function. So, adding a new language will require to restart the app but changing anything for an existing language won't.

If you don't care about hot reload and want to cache the content of each locale, use `Locales.get_cached` instead of `Locales.get`. Keep in mind, however, that all the languages you have will be in memory all the time. Well, not all of them, only 16 recently used ones (using [functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)). If you want to have a smarter caching, make your own wrapper function. You need to find your own balance between performance and memory ocnsumption.
