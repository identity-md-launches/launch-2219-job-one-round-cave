# Uncertainty Lens

Uncertainty Lens turns a small JSON array of timestamp intervals into a reproducible summary of definite pairwise order and unresolved overlaps. It is a local, read-only incident-evidence helper using only Python's standard library. It never runs the services described by the events.

From the repository root, run this one command:

```sh
printf '%s\n' '[{"id":"ingest","start":1,"end":3},{"id":"alert","start":3,"end":4},{"id":"retry","start":2,"end":5}]' | python3 -B line-3/tools/uncertainty-lens/uncertainty_lens.py
```

Tried locally: it reported `ingest` before `alert`, and the two pairs involving `retry` as uncertain. Ten focused tests passed, including CLI rejection of nonfinite JSON numbers, oversized input and paths escaping the workspace, plus all 100 pairs of small integer intervals in both input orders. No real incident or measured clock error is claimed.

Input is a JSON array of objects with a unique, nonempty string `id` and finite, nonboolean numeric `start` and `end`, with `start <= end`. Nonzero intervals are half-open: an end exactly equal to another start gives definite order. A zero-width interval represents an exact timestamp point. Two coincident points remain unresolved with reason `coincident timestamp points`, independent of input order. Distinct points remain ordered; a point inside a nonzero interval remains unresolved. Overlap or coincident readings do not establish simultaneity or causality. Extra object fields are ignored.

The CLI accepts stdin by default or a JSON file path **inside the current working directory**, treated as the workspace root. Absolute paths, `..` paths and symlinks are resolved and rejected before opening if they escape that root. Run from your selected evidence workspace; this path check is not an OS sandbox against concurrent symlink changes. The CLI reads at most 256 KiB and accepts at most 128 events, bounding the report to 8,128 pairs. Malformed input, duplicate IDs, booleans, NaN and infinities fail with an error instead of producing an order claim. JSON numbers use Python's usual integers and binary floats; this tool does not measure clock accuracy or promise arbitrary decimal precision.

Try the fixed coincident-point case:

```sh
printf '%s\n' '[{"id":"ingest","start":3,"end":3},{"id":"alert","start":3,"end":3}]' | python3 -B line-3/tools/uncertainty-lens/uncertainty_lens.py
```

Observed: zero definite orders and one unresolved pair, rather than an input-order-dependent claim. To repeat the checks:

```sh
python3 -B -m unittest discover -s line-3/tools/uncertainty-lens -v
```
