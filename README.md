# l10n

A library and CLI for translating Python applications and libraries.

Features:

+ **Simple**. We stripped away all unnecessary steps and concepts. All that's left is what is actually relevant for Python.
+ **Type-safe**. All other tools match translation.
+ **Explicit**. No global state, no variable injection. You know exactly what gets translated and to what language.
+ **Zero-dependency runtime**. There are a few small dependencies for CLI but they get installed only on your dev environment. On the production goes only one small library, l10n  itself.
+ **Pure Python**. You can use it with PyPy, Numba, and any other interpreter.
+ **Zero configuration**. The tool knows about the modern Python packaging and automatically discovers the project structure, name, version, and all other relevant metadata.
+ **Well documented**. We make sure that you can pick up the tool without any prior knowledge of the topic.
+ **Compatible with other tools**. We use `*.po` and `*.mo` files that are compatible with [gettext](https://www.gnu.org/software/gettext/) toolchain and all other translation tools.
+ **Self-sufficient, no other tools required**.
+ **Asyncio-compatible and race-condition-free**.
+ **Fast**. All teanslations on the production are compiled into a small and fast binary format.
+ **Can be used in libraries**. The compiled translations are automatically placed next to your Python code and discovered at runtime.

## l10n in 30 seconds

Install l10n:

```bash
python3 -m pip install l10n
```

And there are all the changes you need to do in your code to support translations for a string:

```python
from l10n import Locales
locales = Locales()

def say_hello(lang='en'):
    loc = locales[lang]
    msg = loc.get("Hello, world!")
    print(msg)
```

Now, let's translate it to Ukrainian:

1. Extract all strings from the code that need to be translated:

    ```bash
    python3 -m l10n extract --lang ua
    ```

1. Translate all extracted strings using Google Translate:

    ```bash
    python3 -m l10n translate
    ```

1. Compile all translations into the binary format:

    ```bash
    python3 -m l10n compile
    ```

That's all! Now, your code supports translations:

```python
from example import say_hello
say_hello(lang='ua')
```

If you want to manually adjust the translation text, just edit the `languages/en.po` file and run `compile` again. You don't even need to restart your app!
