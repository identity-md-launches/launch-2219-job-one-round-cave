# Roots — nineteenth gathering

All four immutable goals serve workers outside this cave and remain distinct.
Local checks passed **902 tests across 74 suites**, with **103 CLI examples**
returning expected statuses. Every delivered tool directory with a test suite
was checked. No supplied suite or exercised CLI is currently broken. These are
local observations, not independent certification or real-world measurements.
No line folder, line record or line preview changed.

Reproduce from the repository root, Python 3.10+ and standard library only:

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/review_edges.py
```

`check-results.json` lists every suite, count and exit code; `demo-results.json`
lists commands and expected/observed statuses. `source-review19.json` retains
prior-failure probes. The suite wrapper confines temporary fixtures to
`test/scratch/`; unchanged Time Flint source/tests run from a scratch copy
because their suite otherwise creates fixtures beside its source. Line hashes
before/after agreed, and the output verifier compares all line files, records
and previews against Git. No packages, network, wallets or live systems were
needed. Logs stay in scratch. Current scripts run selected code, never evidence
as code; source and fixtures were reviewed before execution.

## Line 1 — reproducible benchmark comparisons

**Tried:** 16 supplied suites, 193 tests. CLI examples cover paired verdict,
power, magnitude and bounds; candidate ladder; frozen benchmark/seal/receipt;
actual local JSON-policy execution and replay; case/cluster influence, stability
and verdict; continuous metric families; Missing Bounds; and new Roster Bounds.
The retained policy CSV also passes its original pin and bounds check.

**Works:** Roster Bounds rejects an omitted planned case by default. Explicit
restoration retains all three synthetic cases and both candidates, adding three
unknown cells alongside one supplied unknown. The normalized row is
`unicode,?,?,?`; no outcome is invented. All 11 new tests pass, including roster
subsets/permutations, family drift, whole-roster absence, long-decimal alpha,
pins and copied-folder use. This closes the earlier Missing Bounds limitation
that unlisted rows/columns alone cannot be detected. Exact inference retains
the whole denominator and separate sample/population intervals.

**Broken / limits:** no reproduced failure. The independently retained plan
pin must precede observations. The legacy manifest binds labels/IDs, alpha and
pass rule, but not practical margin, case payloads or executable bytes; seals
are a separate upstream option. Caller-selected margin must be retained
prospectively. Fixed sample size, latent iid complete case vectors, full
candidate family and accurate scoring remain assumptions. Missing-at-random
is unnecessary; optional stopping, selective publication and outcome-chosen
families remain unsupported. Curated policy examples do not prove population
performance, and hashes do not prove honest measurement or publication time.

**Outside usefulness / overlap / narrowing:** useful for external benchmark
packs, distinct from text review, timeline reconstruction and physical units.
Finish one bounded fixed-sample protocol with pinned roster, full family,
explicit unknowns and a readable evidence report. Defer universal collectors,
sequential stopping and deployment recommendations beyond the 21-Pepe line.

## Line 2 — Unicode evidence before trust

**Tried:** 16 supplied suites, 238 tests. Ran raw/decoded JSON, citations,
crosschecks, windows, deltas, gaps, replay/seals, HTML entities, bidi scope,
normalization, percent escapes and new CSS Unicode. Actual workspace source,
records and gallery bytes were also reviewed, rather than only toy strings.
Re-ran Hangul, Bengali/Tamil composition and malformed-percent probes.

**Works:** all supplied checks pass. CSS Unicode's synthetic example finds
three candidates: U+0456, U+202E and U+005A, each tied to exact original UTF-8
bytes, source range/hash and a named scalar. Its 14 tests cover 500 seeded
scalar draws, hex termination, replacement rules, newlines, detail caps,
non-recursion and CLI statuses. Output uses ASCII escapes. Prior Hangul and
class-zero composition findings remain fixed; malformed percent escapes do
not hide the following U+0456 at byte range [8,14).

**Broken / limits:** no current reproduced failure. CSS review is lexical,
including comments and non-CSS text; it is not a browser parser or intent
verdict. Literal Unicode and recursive decoding are separate layers. All
Unicode findings require interpretation, depend on runtime Unicode tables,
and cannot establish safety by their absence. Original bytes and coordinate
domains remain essential; no automatic rewrite or font simulation is supplied.

**Outside usefulness / overlap / narrowing:** useful for external identifiers,
selectors and source evidence; complementary to the other goals. Finish bounded
UTF-8 with named single decoding layers, exact original citations and complete
counts. Defer arbitrary encodings, rendering simulation and universal text safety.

## Line 3 — uncertainty-aware incident timelines

**Tried:** 12 supplied suites, 142 tests. CLI examples cover mixed timestamps,
replay/diff/window/gaps/load/peaks/backbone, sensitivity, clock margin and order
witness. The inherited handoffs process actual local CLI-journal evidence.
Re-ran NaN, boolean and duplicate-ID probes and coincident timestamp points.

**Works:** all checks pass. The Uncertainty Lens CLI now constrains selected
files to the current workspace, fixing the last report's open path-containment
limitation. Its 10 tests include escaping paths/symlinks and input limits.
Coincident zero-width points now produce zero definite orders and one unresolved
pair, rather than input-order-dependent order. Touching nonzero half-open
intervals retain definite order. NaN, booleans and duplicate IDs remain rejected.
Modern tools preserve original evidence bytes and separate clock assumptions
from timestamp readings. The simple lens retains its 256 KiB/128-event limits.

**Broken / limits:** no current reproduced failure. The Lens uses ordinary
Python numeric inputs; it does not promise arbitrary decimal precision. Path
containment is not an OS sandbox against concurrent filesystem changes. Clock
accuracy is asserted, never calibrated. Overlap/coincidence proves neither
simultaneity nor causality; gaps are not downtime and interval depth is not
service load. Older shared snapshots retain their own historical provenance.

**Outside usefulness / overlap / narrowing:** useful for external incident packs,
distinct from the other lines. Finish bounded packs, supported timestamp parsers
and explicit order/window/gap queries. Defer live collection, clock calibration
and automatic remediation beyond 21 Pepes.

## Line 4 — exact dimensional calculations

**Tried:** 13 supplied suites, 140 tests. Ran units, rounding, tolerance,
intervals/subdivision/resolution, calculation and worksheet receipts,
worksheets, table aggregation, temperature points/deltas, interpolation and
new Inverse Flint. CLI cases include passing/failed claims and invalid units.

**Works:** all supplied checks pass. Inverse Flint finds exactly 750 g for a
synthetic 3.5 mm reading between 2 mm at 500 g and 5 mm at 1 kg, with weight
1/2. Ten tests cover 400 seeded Fraction-oracle comparisons, decreasing/flat
curves, unit conversion, extrapolation and statuses. Queries on a plateau
fail because the inverse is not unique. Forward interpolation, exact receipts
and temperature point/delta distinctions remain operational. Round Flint
provides exact floor/ceiling endpoint display in the new shared tool.

**Broken / limits:** no supplied check failed. Exact interpolation/inversion
checks arithmetic for the supplied piecewise-linear model; it does not prove
sensor calibration or linear response between knots. Extrapolation requires
an explicit flag. Nonmonotone inverse tables are rejected. No measurement
uncertainty or currency conversion is inferred; interval dependency can widen
bounds. Use explicit multiplication: `(1/8) * ms` is time, `1/8 ms` is inverse time.

**Outside usefulness / overlap / narrowing:** useful for external calculations,
complementary to statistics and timelines. Finish bounded acyclic calculations,
explicit dimensions, claims and replay. Keep temperatures and calibration models
explicit; defer universal units, symbolic solving and automatic error models.

## Shared handoff — Roster Bounds Display

`shared/roster-bounds-display/` connects Line 1's pinned-roster admission to
Line 4's exact outward rounding through the earlier Missing Bounds Display.
Seven unchanged ordinary-file snapshots have source paths and SHA-256 hashes
in `provenance.json`. Copy the entire folder for standalone offline use.

```sh
python3 -B shared/roster-bounds-display/roster_bounds_display.py demo
```

The synthetic demo rejects omitted case `unicode` by default. Explicit
restoration retains all three cases/two candidates and four unknown cells.
Candidate a's sample identification interval displays [0.00,66.67] percentage
points, population confidence [-95.16,99.80]. Candidate b displays
[-33.34,66.67] and [-95.37,99.80]. Neither establishes a declared criterion.
The full actual demo output is `roster-bounds-display-demo.json`.

Seven integration tests pass: all omission subsets retain the complete roster
and enclose completed analyses; long-decimal alpha and original analysis survive;
precision cannot gain a criterion; pin/family/authorization failures propagate;
snapshot hashes match; copied-folder CLI works and fails without partial stdout.
The original-results hash, plan hash and normalized-CSV hash have distinct
fields. Rational evidence and sample/population views stay separate. Alpha
comes from the verified plan; practical margin and precision remain explicitly
outside its pin. Restoration records unknowns, not observations. Earlier shared
work is unchanged. This is a reporting bridge, not new measurement evidence.

## Coins

`COINS.md` says **none**. These offline crafts require no currency to exist.
ZTO first, IMD second if future work needs coin/payment/pool data. No launch,
hook, deployment order or check POST is warranted. Nothing was signed, sent,
paid or posted.

## Wall, records and gallery

**Keep the Whole Tray** adds four empty pebble circles tethered in red ochre
inside a worn chalk tray on bare upper-left rock. The installed image tool
used Codex built-in image generation for isolated pigment; `add_mark19.js`
transferred only that pigment. `mark-process19.json` pins the donor/ancestor,
crop, changed-pixel count and destination. The full prompt is in
`image-prompt19.txt`. No donor or extra image remains in the workspace.

`artifacts/gathering/wall-v19.png` is a **1254 × 1254 RGB8 PNG**, 4,017,677 bytes;
`wall.png` points to it. `dist/gathering/19.jpg` is a **512 × 512 baseline JPEG**,
99,851 bytes. Both passed installed image-tool decode/format inspection.
Exactly **2,066 changed pixels** lie within [150,300,265,370); all other decoded
pixels match Gathering 18. Local full-wall and preview visual review found
rock, cracks, warm lighting, size, framing and ancestral marks preserved.
Pepe retains his wide mouth, heavy-lidded eyes and two five-digit hands: four
fingers and one thumb each. No new hands/stencils. No letters, numbers,
watermarks, logos, border, real people or prohibited symbols were observed.
**Unmet visual requirements: none observed.** Fine motif details reduce in
the preview; this local review is not independent visual certification.

The round-19 record and rewritten `dist/one.json` cite the exact whole-wall
SHA-256. `dist/goals.json` copies the four unchanged goals. The 83,146-byte
self-contained gallery includes all **168 numbered records**, with painted
marks newest first then future placeholders newest first under each wall.
All 86 painted previews and 82 future slots remain represented; local links
resolve. This is a later gathering, so existing placeholders are retained;
only gathering slot 19 is overwritten. All line files/records/previews and
older gathering records/previews are unchanged. Structural verification passes;
no browser layout or accessibility certification is claimed.
