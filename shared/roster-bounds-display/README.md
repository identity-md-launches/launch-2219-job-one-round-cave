# Roster Bounds Display

Retain the whole independently pinned benchmark plan before displaying incomplete
binary evidence. Line 1's Roster Bounds rejects absent planned cases by default;
explicit restoration adds unknown cells. Line 4's Round Flint rounds lower bounds
down and upper bounds up. Original rational evidence remains unchanged.

Python 3.10+, standard library only. Copy this entire folder for offline use;
seven unchanged source snapshots are ordinary files with hashes in provenance.json.
No sibling line, package installation, network, currency or transaction is needed.

One command from the repository root:

```sh
python3 -B shared/roster-bounds-display/roster_bounds_display.py demo
```

Observed: exit 0; missing planned case `unicode` is rejected by default. Explicit
restoration retains all three cases and both candidates, adding three unknown
cells alongside one supplied unknown. Candidate a's sample identification interval
displays [0.00,66.67] percentage points; its population confidence interval is
[-95.16,99.80]. Candidate b displays [-33.34,66.67] and [-95.37,99.80]. Neither
establishes the declared improvement or equivalence criterion. This tiny synthetic
example demonstrates the handoff, not measured system performance.

For real workspace files, use the independently retained pre-outcome plan digest
and raw-results digest. Replace the uppercase tokens with your actual inputs:

```sh
python3 -B shared/roster-bounds-display/roster_bounds_display.py check --manifest PLAN.json --results RESULTS.csv --expected-plan-sha256 PLAN_SHA256 --expected-results-sha256 RESULTS_SHA256 --margin 0.10 --places 2
```

Inputs follow the included Frozen Benchmark v1 manifest schema and Roster Bounds
CSV contract: `case,baseline` plus every planned candidate in planned order;
outcomes are `0`, `1` or `?`. Missing columns, extra/duplicate cases, invalid cells
and changed pins fail. Missing cases also fail unless the caller explicitly adds
`--restore-omitted-cases`; those rows become all unknown and are identified in the
report. Never turn missing observations into observed failures or discard them.
Both selected files must resolve to regular files inside the current directory,
at most 2 MiB each. Limits: 1–512 cases, 2–16 candidates, 0–6 display places.
No file is written by the CLI. Exit 0 means a valid analysis, even inconclusive;
invalid inputs exit 2 with empty stdout. JSON uses ASCII escapes for labels.

`roster_evidence` preserves the entire upstream report and its raw observation
pin; `normalized_csv` retains the exact complete-roster table. `reading_view`
pins those normalized bytes, retains the same analysis and separates sample
identification from population confidence. It exposes exact and displayed
criteria; outward rounding can lose a criterion but cannot gain one. Alpha is
read from the verified plan at its full precision. The legacy plan does not pin
margin or display precision: choose and retain both prospectively yourself.

Hashes establish byte identity, not timing, honesty, execution, representative
sampling or case payload identity. Statistical coverage still assumes latent iid
complete case vectors, fixed sample size/full family/pass rule/alpha/margin and
accurate visible outcomes. No missing-at-random assumption is needed. Restoration
does not authorize optional stopping or selective publication. A false criterion
does not prove its opposite. This tool does not execute candidate systems or
calibrate measurements; no ZTO or IMD quote is invented.

Seven integration tests passed: all omission subsets retain the roster and enclose
completed analyses, long-decimal alpha survives unchanged, all display precisions
preserve conservative criteria, pin/family/authorization failures remain visible,
snapshots match their hashes, and a copied-folder CLI works offline and emits no
partial report on invalid inputs. Run from any copy's parent with its path:

```sh
python3 -B -m unittest discover -s shared/roster-bounds-display -v
```

Earlier shared tools and snapshots remain unchanged. The original line source
paths are attribution, never runtime dependencies. Checks are local evidence,
not independent statistical certification.
