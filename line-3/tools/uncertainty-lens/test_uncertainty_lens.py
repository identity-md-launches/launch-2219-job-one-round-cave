import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from uncertainty_lens import MAX_EVENTS, MAX_INPUT_BYTES, analyze


SCRIPT = Path(__file__).with_name("uncertainty_lens.py")


class LensTests(unittest.TestCase):
    def test_touching_is_ordered_and_overlap_is_uncertain(self):
        out = analyze([{"id": "a", "start": 0, "end": 2},
                       {"id": "b", "start": 2, "end": 4},
                       {"id": "c", "start": 1, "end": 3}])
        self.assertIn({"before": "a", "after": "b"}, out["definite_orders"])
        self.assertEqual(out["uncertain_pairs"], [
            {"events": ["a", "c"], "reason": "intervals overlap"},
            {"events": ["b", "c"], "reason": "intervals overlap"}])

    def test_bad_interval(self):
        with self.assertRaises(ValueError):
            analyze([{"id": "bad", "start": 2, "end": 1}])

    def test_coincident_points_never_invent_order(self):
        a = {"id": "a", "start": 4, "end": 4}
        b = {"id": "b", "start": 4, "end": 4}
        for events in ([a, b], [b, a]):
            result = analyze(events)
            self.assertEqual(result["definite_orders"], [])
            self.assertEqual(len(result["uncertain_pairs"]), 1)
            self.assertEqual(result["uncertain_pairs"][0]["reason"],
                             "coincident timestamp points")

    def test_distinct_points_and_point_at_boundary(self):
        a = {"id": "a", "start": 2, "end": 2}
        b = {"id": "b", "start": 3, "end": 3}
        for events in ([a, b], [b, a]):
            self.assertEqual(analyze(events)["definite_orders"],
                             [{"before": "a", "after": "b"}])
        interval = {"id": "interval", "start": 0, "end": 2}
        self.assertEqual(analyze([a, interval])["definite_orders"],
                         [{"before": "interval", "after": "a"}])
        spanning = {"id": "span", "start": 1, "end": 4}
        self.assertEqual(analyze([a, spanning])["definite_orders"], [])

    def test_cli_workspace_paths_and_symlink_escape(self):
        # All fixtures stay in the assignment's explicitly allowed scratch area.
        scratch = Path("test/scratch")
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory).resolve()
            workspace = root / "workspace"
            workspace.mkdir()
            payload = '[{"id":"local","start":1,"end":2}]'
            (workspace / "events.json").write_text(payload, encoding="utf-8")
            for name in ("events.json", str(workspace / "events.json")):
                proc = subprocess.run([sys.executable, "-B", str(SCRIPT.resolve()), name],
                                      cwd=workspace, capture_output=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(json.loads(proc.stdout)["events"], 1)
            (workspace / "escape.json").symlink_to(root / "absent.json")
            for name in ("../absent.json", str(root / "absent.json"), "escape.json"):
                proc = subprocess.run([sys.executable, "-B", str(SCRIPT.resolve()), name],
                                      cwd=workspace, capture_output=True)
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn(b"inside the current workspace", proc.stderr)

    def test_pair_partition_and_reversal(self):
        # Exhaust all small integer intervals, including exact points.
        intervals = [(a, b) for a in range(4) for b in range(a, 4)]
        for a, b in intervals:
            for c, d in intervals:
                left = {"id": "a", "start": a, "end": b}
                right = {"id": "b", "start": c, "end": d}
                forward = analyze([left, right])
                reverse = analyze([right, left])
                self.assertEqual(forward["definite_orders"], reverse["definite_orders"])
                self.assertEqual(len(forward["definite_orders"]) +
                                 len(forward["uncertain_pairs"]), 1)
                if a == b == c == d:
                    self.assertEqual(forward["definite_orders"], [])

    def test_nonfinite_boolean_and_duplicate_ids_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), True, False):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "finite nonboolean"):
                analyze([{"id": "a", "start": value, "end": 2}])
            with self.subTest(end=value), self.assertRaisesRegex(ValueError, "finite nonboolean"):
                analyze([{"id": "a", "start": 0, "end": value}])
        with self.assertRaisesRegex(ValueError, "duplicate event id"):
            analyze([{"id": "same", "start": 0, "end": 1},
                     {"id": "same", "start": 1, "end": 2}])

    def test_array_and_event_limits(self):
        with self.assertRaisesRegex(ValueError, "JSON array"):
            analyze({"id": "a", "start": 1, "end": 2})
        events = [{"id": str(i), "start": i, "end": i + 1} for i in range(MAX_EVENTS)]
        out = analyze(events)
        self.assertEqual(len(out["definite_orders"]), MAX_EVENTS * (MAX_EVENTS - 1) // 2)
        with self.assertRaisesRegex(ValueError, "too many events"):
            analyze(events + [{"id": "extra", "start": 0, "end": 1}])

    def test_cli_rejects_nonfinite_json_and_oversize_input(self):
        for payload in (b'[{"id":"a","start":NaN,"end":2}]',
                        b'[{"id":"a","start":0,"end":Infinity}]',
                        b" " * (MAX_INPUT_BYTES + 1)):
            with self.subTest(payload=payload[:60]):
                proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"],
                                      input=payload, capture_output=True, check=False)
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn(b"error:", proc.stderr)

    def test_cli_demo_is_stable(self):
        payload = b'[{"id":"first","start":1,"end":2},{"id":"second","start":2,"end":3}]'
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"],
                              input=payload, capture_output=True, check=True)
        self.assertEqual(json.loads(proc.stdout)["definite_orders"],
                         [{"before": "first", "after": "second"}])


if __name__ == "__main__":
    unittest.main()
