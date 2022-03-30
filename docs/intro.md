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
flit install --deps=develop
```

The environment is ready! It's time to write some code.

## Writing code

...

## Extracting messages

...

## Translating messages

...

## Compiling messages

...

## Next steps

...
