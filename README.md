# l10n

A library and CLI for translating Python applications and libraries.

Features:

+ **Simple**. We stripped away all unnecessary steps and concepts. All that's left is what is actually relevant for Python.
+ **Type-safe**. All other tools match translation.
+ **Zero-dependency runtime**.
+ **Zero configuration**.
+ **Well documented**.
+ **Compatible with other tools**.
+ **Self-sufficient, no other tools required**.
+ **Asyncio-compatible and race-condition-free**.
+ **Fast**.
+ **Can be used in libraries**.

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
