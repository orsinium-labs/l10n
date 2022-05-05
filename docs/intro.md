# Getting Started

## Modern Python packaging

You might be familiar with [requirements.txt](https://pip.pypa.io/en/stable/user_guide/#requirements-files) or [setup.py](https://setuptools.pypa.io/en/latest/userguide/quickstart.html#basic-use) for describing your project dependencies. Since then, a lot has changed in the Python world. At some point, we had multiple tools like [poetry](https://python-poetry.org/), [pipenv](https://pipenv.pypa.io/en/latest/), [dephell](https://github.com/dephell/dephell), [flit](https://github.com/pypa/flit), and so on, each with its own file format. Luckily, now everyone is settled on a singe universal approach. There are the standards that set the ground:

+ [PEP 517](https://peps.python.org/pep-0517/) introduced `pyproject.toml` as a single configuration file for all Python tools.
+ [PEP 518](https://peps.python.org/pep-0518/) intorduced a `[build-system]` section in `pyproject.toml` that says what tool should be used to buid your project.
+ [PEP 621](https://peps.python.org/pep-0621/) intorduced a `[project]` section in `pyproject.toml` that described all project metadata, like name, version, authors, dependencies.

You don't have to use all this to work with l10n but if you do, l10n will be better at finding your project metadata. In this section, we will use the modern packaging approach for all examples.

## Installation

Let's start a new project:

```bash
mkdir l10n-playground
cd l10n-playground
```

Now, let's create a `pyproject.toml` with your project metadata and add `l10n` into dependencies. In this example, we will use [flit](https://flit.pypa.io/en/latest/) for dependency management.

Add into `pyproject.toml`:

```toml
[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "l10n_playground"
dynamic = ["version", "description"]
requires-python = ">=3.7"
dependencies = ["l10n"]

[project.optional-dependencies]
dev = ["l10n[cli]"]
```

And into `l10n_playground/__init__.py`:

```python
"""Experimenting with l10n"""

__version__ = "1.0.0"
```

Now, you can install your project:

```bash
python3 -m pip install -U flit
flit install --deps=develop --symlink
```

The environment is ready! It's time to write some code.

## Writing code

In l10n, your code is the single source of truth, and translation files are generated from it. So you always start from writing code, and translations go later.

The class `Locales` provides a runtime catalog of translation for different languages. Create an instance of it (usually, no need to pass any arguments, defaults are good) and use it as mapping where keys are language codes. Sounds vague so far, so let's get our hands dirty.

Create `l10n_playground/example.py`:

```python
from argparse import ArgumentParser
from l10n import Locales

locales = Locales()

def say_hello(lang: str = 'en') -> None:
    loc = locales[lang]
    msg = loc.get('Hello, world!')
    print(msg)

def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--lang', default='en')
    args = parser.parse_args()
    say_hello(lang=args.lang)
```

And `l10n_playground/__main__.py`:

```python
from .example import main

main()
```

If you try to run it, it will fail with `KeyError` because there is no `en` language in the catalogue. So, it's time to make some.

## Extracting messages

Now, let's generate translation files from our code for English and Russian:

```bash
python3 -m l10n extract --lang=en
python3 -m l10n extract --lang=ru
```

These commands will create `locales/en.po` and `locales/ru.po` respectively. PO file format is a standard text format for translations introduced in [GNU](https://www.gnu.org/) (Linux) and used in many places. it's kind of a de facto standard for translations, so it's supported by most of the tools. But since it's a text format, you can open it in any text editor, it's very readable. Inside, you'll see some headers (feel free to edit them) and the text message to be translated extracted from your code. Now, it's time to translate.

## Translating messages

At this point, we have a file to store translations. The file contains the messages from our code (currently, only `"Hello, world!"`) but no actual translation. Usually, this is where you send the file to a translator and forget about it while they are doing their job. But if you don't have a translator just yet, don't worry, we've got you covered.

English you can translate yourself, just edi `en.po` file in any text editor:

```elixir
#: ./l10n_playground/example.py:9
msgid "Hello, world!"
msgstr "Hello, world!"
```

And for Russian, we'll use `l10n translate` command which will automatically translate all messages using [Google Translate](https://translate.google.com/) unofficial API:

```bash
python3 -m l10n translate
```

And this is what you now sohuld see in `ru.po`:

```elixir
#: ./l10n_playground/example.py:9
#, fuzzy
msgid "Hello, world!"
msgstr "Привет, мир!"
```

Now, it's time to get it back into your app.

## Compiling messages

PO file format is a readable text format for humans. For machines, we need mo files which are binary and optimized for machines. The po files are used by you and translators during the app development, mo files are used by your app (or library) to get translations for messages in runtime. So, before we can run the app, we need to compile mo files:

```bash
python3 -m l10n compile
```

The command will create `en.mo` and `ru.mo` binary files inside of `l10n_playground/locales/`.

## Running the app

Now, it's time to run the app!

```bash
$ python3 -m l10n_playground
Hello, world!
$ python3 -m l10n_playground --lang=ru
Привет, мир!
```

It works!

## Updating messages

When you update a message or add a new one:

+ Run `l10n extract` to update po files. No need to specify `--lang`, by default it will just update all po files you already have.
+ Run `l10n translate` if you want it to be auto-translated (or translate it manually).
+ Run `l10n compile` to generate mo files.

## Cheat sheet

+ po file is a text file with translations.
+ mo file is a binary file compiled out of mo files.
+ `l10n.Locales` is a mapping of locales (mo files) with language codes as keys.
+ `l10n extract --lang=nl` to generate po file for `nl` langauge.
+ `l10n extract` to update all po files you have.
+ `l10n translate` to run Google Translate on all po files you have.
+ `l10n compile` to generate mo files from po files.

See also the [advanced usage](./advanced.md) to get more out of l10n.
