# CSS Unicode

Expose Unicode hidden in CSS-style backslash escapes before publishing a
selector or trusting an identifier. Each candidate has its exact original
UTF-8 byte range, source hex, SHA-256, line/byte column, escape form, written
hex value and decoded scalar name/category. Printable ASCII escapes are also
retained: escaped punctuation or letters can matter even without Unicode.

Python 3.9+; standard library only. No install, network, execution of input,
rewrite, keys or transactions. Copy this entire folder for standalone use.

From the repository root, run this synthetic demonstration:

```sh
python3 -B line-2/tools/css-unicode/css_unicode.py --demo
```

Observed: three candidates, U+0456 CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN
I, U+202E RIGHT-TO-LEFT OVERRIDE, and U+005A LATIN CAPITAL LETTER Z. The first
is concealed in an `admin` lookalike; this is a labeled example, not a detected
attack. Output is ASCII JSON, so directional characters are never emitted raw.

For actual selected workspace text:

```sh
python3 -B line-2/tools/css-unicode/css_unicode.py --file dist/index.html --max-details 20
```

`--file` must resolve to a regular file inside the current working directory.
Only that file is read, bounded at 2 MiB. A file review exits 1 when candidates
exist, 0 when none exist, and 2 on invalid input. The demo exits 0. The detail
cap (0–1000) never truncates counts or analysis. Ranges are zero-based half-open
original bytes; lines/byte columns are one-based and LF-only.

Hex escapes consume one to six digits, then at most one CSS whitespace
terminator (CRLF counts as one newline). Zero, surrogate and out-of-range
values produce U+FFFD while preserving the original written value. Simple
escapes consume one scalar. Backslash-newline and end-of-input have no asserted
decoded scalar: CSS string continuations and invalid identifier escapes need
context. Non-overlapping escapes are scanned once; there is no recursive decode.

This is lexical evidence, **not a CSS parser or safety verdict**. Comments,
strings and non-CSS text are intentionally scanned alike; browser treatment,
HTML embedding, identifier grammar, literal Unicode and font confusability
are outside scope. Legitimate CSS commonly contains escapes. Zero candidates
cannot establish safety; a hash establishes byte identity, not authenticity.

Local check: 14 tests passed, including 500 seeded scalar draws checked against
Python's UTF-8 encoding, exact byte citations, replacement rules, all CSS
whitespace terminators, newline context, six-digit limits, non-recursion,
complete capped counts, input validation and CLI statuses:

```sh
python3 -B -m unittest discover -s line-2/tools/css-unicode -v
```
