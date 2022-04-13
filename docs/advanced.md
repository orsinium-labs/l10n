# Advanced usage

## If translation is missed

...

## Plural form

...

## Fuzzy entries

...

## Keeping translations up-to-date

...

## Including additional strings

...

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

## Translating HTML

...
