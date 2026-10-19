# Roster Bounds

Keep an incomplete binary benchmark attached to its **whole planned case set
and candidate family** before computing Missing Bounds. This closes a handoff
gap: Missing Bounds cannot detect rows or columns that were never supplied,
while Frozen Benchmark only admits complete binary outcomes. Python 3.10+,
standard library only; copy this entire folder for standalone offline use.

From the repository root, one command shows it working:

```sh
python3 -B line-1/tools/roster-bounds/roster_bounds.py demo
```

When tried, the synthetic fixture's two supplied rows omitted planned case
`unicode`. Default checking rejected it. Explicit restoration retained all
three planned cases and both candidates: three restored unknown cells plus
one supplied unknown, four unknown cells total. The normalized CSV includes
`unicode,?,?,?` in planned order. No outcome was invented; neither candidate
established a practical criterion. These are illustrative data, not measured
performance. `example-result.json` retains the actual demo output.

## Use your existing prospective protocol

Use a Frozen Benchmark v1 manifest and its independently retained **pre-outcome**
`plan_sha256`. Its full schema and freezing implementation are included unchanged
in `frozen_engine.py`; the predecessor README explains the protocol. The plan
must contain the complete case roster, baseline version, candidate versions,
pass rule and alpha. Keep the actual payloads and system bytes separately, or
use Benchmark Seal upstream. This checker binds IDs and labels, not asset bytes.

Supply UTF-8 CSV headed `case,baseline` followed by **all** planned candidate
names in their original order. Each outcome must be `0`, `1`, or explicit `?`.
Rows may be reordered, with Unicode/comma-containing IDs quoted as CSV. An
unknown baseline stays unknown and affects every comparison. Missing candidate
columns, renamed/reordered candidates, extra cases, duplicate cases, blank rows,
invalid outcomes and ragged rows always fail. Missing planned cases fail by
default. Even an entirely unknown candidate must keep its column.

Replace uppercase tokens below with your actual workspace-relative files and
retained digests. This command prints the report and changes no file:

```sh
python3 -B line-1/tools/roster-bounds/roster_bounds.py check --manifest PLAN.json --results RESULTS.csv --expected-plan-sha256 RETAINED_PLAN_SHA256 --expected-results-sha256 RETAINED_RESULTS_SHA256 --margin 0.10
```

Retain the raw results SHA-256 independently at handoff. The plan pin detects
plan replacement; the results pin detects changed raw observations. Neither
pin establishes publication time, accurate scoring, execution or honesty.
**Alpha is taken from the verified plan**, without a CLI override. The older
protocol has no practical-margin field: `--margin` is explicitly **not covered
by its pin**. Choose and retain that margin prospectively through your review
process; do not tune it to observed results. Margin defaults to 0.10, accepts
plain decimal 0–1 with at most nine fractional places, and is an absolute
pass-rate difference.

If a genuinely lost/unavailable case row must remain in the evidence, explicitly
append `--restore-omitted-cases`. That restores every absent planned case with
unknown outcomes for baseline and all candidates, and reports each restored ID,
the added unknown-cell count, supplied unknown count and authorization flag.
It never scores these rows as observed failures or silently drops them. The
entire planned set remains the denominator. Restoration also works for a
header-only input, yielding the whole roster as unknown and bounds [-1,+1].
Choose whether a timeout is an observed failure or an unknown in the prospective
pass rule; this tool cannot decide that scientific question for you.

Append `--emit-csv` to print **only** the normalized complete-roster CSV instead
of JSON. All checks and analysis finish before stdout is written. The report's
`normalized_csv_sha256` equals the embedded analysis's `input_sha256` and the
hash of those exact emitted bytes. Preserve the raw files and report too;
normalization changes order, quoting and line endings. Exit 0 means valid
analysis, including inconclusive results. Invalid input exits 2 with stderr
and empty stdout. Never reuse stale redirected CSV after a failed command.

## Statistical and input boundaries

This wrapper introduces no new statistical method: its unchanged Missing Bounds
snapshot encloses all binary completions using outward exact binomial bounds.
The familywise tail budget retains every candidate. Unknowns may depend on
outcomes; no missing-at-random model is introduced. The interpretation still
requires latent iid case vectors, a fixed prospective family/sample size/pass
rule/alpha/margin, accurate visible outcomes and no selective publication or
optional stopping. Do not repeatedly analyze a filling table to choose when to
stop. Sample identification intervals and population confidence intervals remain
separate fields. Curated cases alone do not establish population performance.

Limits are the intersection of the two predecessor protocols: 1–512 cases,
**2–16 candidates**, and case/candidate labels of 1–200 characters without edge
whitespace or Unicode category-C characters. The original baseline/pass-rule
limits remain 256/8,192 characters. Alpha retains the original plan's exact
decimal precision, up to 18 fractional places, within 0.000001–0.2. Each input
is bounded at 2 MiB and must resolve to a regular file within the current
working directory; escaping symlinks fail. This is not a sandbox against an
adversary concurrently changing filesystem entries. Duplicate JSON members,
unknown manifest/plan keys and self-consistent replacement plans fail against
the retained plan pin. No file is downloaded or executed; no environment,
wallet, key, payment, pool, transaction or currency is needed.

## Local checks and reuse

```sh
python3 -B -m unittest discover -s line-1/tools/roster-bounds -v
```

All 11 new tests passed: every omission subset and row permutation of a
three-case roster, full family drift rejection, explicit unknown accounting,
whole-roster absence, malformed inputs, independent pins, UTF-8/BOM/CRLF,
exact long-decimal alpha, 25 seeded downstream comparisons, complete-data
agreement with the original Frozen Benchmark admission, limits and a real
copied-folder CLI with exit/CSV/pin/path/input-immutability checks. The unchanged
Missing Bounds and Frozen Benchmark predecessor suites also passed. These are
local checks, not independent certification.

Three unchanged ordinary-file source snapshots and their SHA-256 pins are
listed in `provenance.json`. Runtime needs no sibling folder or installation.
Earlier tools and their tests are unchanged.
