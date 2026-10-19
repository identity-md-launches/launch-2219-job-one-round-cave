# Inverse Flint

Find the unique input corresponding to a supplied reading in a monotone,
piecewise-linear calibration table. Exact rational arithmetic and explicit
physical dimensions keep the calculation checkable. Python 3.10+ and the
standard library suffice; copy this whole folder to run it offline.

One command from the repository root shows it working:

```sh
python3 -B line-4/tools/inverse-flint/inverse_flint.py demo
```

Tried locally: the command exited **0** and found **750 g** for a hypothetical
3.5 mm reading between 2 mm at 500 g and 5 mm at 1 kg. The right weight is
exactly `1/2`. Ten local tests passed, including 400 seeded comparisons
with an independent `Fraction` oracle, decreasing curves, flat segments,
unit conversion, claims, extrapolation and CLI exit codes. A standalone copy
of the folder also passed its demo and tests. These are local checks, not
independent certification of any supplied calibration.

## Use your table

Send one JSON object to `run` on stdin:

```sh
printf '%s\n' '{"schema":"inverse-flint/1","points":[{"x":"500 g","y":"2 mm"},{"x":"1 kg","y":"5 mm"}],"at":"3.5 mm","to":"g","expect":"750 g"}' | python3 -B line-4/tools/inverse-flint/inverse_flint.py run
```

Required fields are `schema`, `points`, `at` and `to`. Optional fields are
`expect` (an x quantity) and boolean `extrapolate`. Each point has exactly
`x` and `y`. x coordinates must be strictly increasing after conversion;
y values must be monotone, increasing or decreasing, but may include flats.
The whole table is validated. A query that equals a flat segment's y value
is rejected because infinitely many x values would satisfy it. A constant
table has no unique inverse. At a shared nonflat knot, the right segment is
reported except at the final knot. Points are never silently sorted.

For the chosen segment, the result is exactly
`x0 + ((at - y0)/(y1 - y0)) * (x1 - x0)`. The output identifies its point
indices, originals, exact right weight and inverse slope in base units.
`to` changes display only. A query outside the table fails unless
`"extrapolate":true` is supplied; extrapolation uses the first or last
boundary segment and sets `extrapolated:true`. A flat boundary segment cannot
be extrapolated because it gives no unique inverse line at that edge.

Exit **0** means a valid calculation with a passing claim or no claim.
Exit **1** means the supplied `expect` differs. Exit **2** means invalid input
or a resource limit; invalid requests produce no partial stdout.

Expressions support `+ - * / ^ **`, parentheses, exact decimals and integer
powers -12..12. Supported units: m, cm, mm, km, in, ft, mi; kg, g, mg, t;
s, ms, min, h, day; B, KiB, MiB, GiB; L, mL; N, J, W. Use explicit
multiplication around compound quantities: `(1/3) * s` is time, but
`1/3 s` is inverse time. A target unit has positive scale and x dimensions.

Input is limited to 65,536 UTF-8 bytes, four JSON nesting levels and 2..128
points. Duplicate keys, numeric JSON values, extra fields and nonfinite
constants fail. Expressions are limited to 4096 characters, 256 tokens and
32 nesting levels. Exact values and intermediates have a 2048-bit budget;
dimension exponents stay within -256..256. These bounds may reject a valid
mathematical result.

This verifies arithmetic **for a supplied piecewise-linear model**. It does
not establish that a sensor is accurate, that a response is linear between
points, or that an extrapolated value is physically valid. Nonmonotone tables
can have multiple inverse answers and are deliberately rejected. No input
uncertainty, currency conversion, wallet or transaction is involved; no ZTO
or IMD price is invented. The tool reads stdin and its own code only, writes
stdout/stderr only, and does not access environment variables or the network.

`engine.py` is an unchanged ordinary-file snapshot of the inherited Unit
Flint engine, so this folder needs no sibling tools, packages or submodules.
Run its checks with:

```sh
python3 -B -m unittest discover -s line-4/tools/inverse-flint -v
```
