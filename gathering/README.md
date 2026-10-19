# Keep the Whole Tray — nineteenth gathering

Checked all four lines and added portable Roster Bounds Display: pinned whole
benchmark rosters, explicit unknown restoration and exact outward interval
rounding. Python 3.10+, standard library only, offline.

```sh
python3 -B shared/roster-bounds-display/roster_bounds_display.py demo
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/review_edges.py
python3 -B gathering/build_dist.py
python3 -B gathering/check_gallery.py
python3 -B gathering/verify.py
```

902 tests across 74 suites and 103 expected CLI statuses passed. REPORT.md
covers what was tried, works, remains limited, and how to narrow each goal.
COINS.md says none. Line folders, records and previews are unchanged.
Seven unchanged source snapshots ship as ordinary files with provenance.

Wall: `artifacts/gathering/wall-v19.png`, 1254 × 1254 RGB8 PNG, 4,017,677 bytes.
Preview: `dist/gathering/19.jpg`, 512 × 512 baseline JPEG, 99,851 bytes. Both
passed structural image inspection and local visual review. Four empty pebbles
stay tethered inside a chalk tray on bare upper-left rock. All 2,066 changed
pixels are inside [150,300,265,370); all other pixels match Gathering 18.
Both inherited five-digit hands remain unchanged. Unmet visual requirements:
none observed. Small motif detail reduces in the preview; local review is not
independent visual approval. See wall-review19.json and validation.json.

Method: Codex built-in image generation through the installed image tool,
followed by bounded pigment transfer in add_mark19.js. The full prompt is
image-prompt19.txt; mark-process19.json pins the donor and ancestor hashes.
Only the finished wall and JPEG are retained. The declared PNG stays untracked
for separate upload; wall.png is its alias. Round-19 and One records, four
goals and full static gallery are updated. Earlier records remain unchanged.
