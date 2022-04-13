# What we stripped away

The usual workflow for translating apps is pretty complex. We made it simple by removing some of the steps that don't bring much of a value in a regular translation pipeline. Our design philosophy is "make simple simple, make complex possible". There are some of these things:

+ The compiled translations are stored next to your Python code instead of `/usr/share/locale`.
+ We don't generate `*.pot` files. Instead, we directly create empty `*.po` files for all languages.
+ You don't need to explicitly update translations for each language. Instead, the `extract` command updates all translation files in place.
+ There is only one translation file per project per language. No need to merge multiple files together.
+ There is no `LC_MESSAGES` subdirectory because "flat is better than nested".
+ There is only one `.get` method instead of the whole mess of similar ones (`gettext`, `ngettext`, `pgettext`, and so on) provided by [gettext](https://docs.python.org/3/library/gettext.html).
+ The locale doesn't have categories. While UNIX and other OS allow to specify locale for each action (`LC_TIME` for formatting time, `LC_NUMERIC` for formatting numbers), we make one-to-one correspondence between locales and categories. If you need to format a number in a different locale, just use a separate Locale instance for it.
