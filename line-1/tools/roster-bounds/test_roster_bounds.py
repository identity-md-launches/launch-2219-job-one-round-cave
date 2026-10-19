"""Roster conservation, independent enumeration, pins and portable CLI checks."""
import csv
import hashlib
import io
import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as F
import roster_bounds as r


def fixture(cases=('first', 'second', 'third'), candidates=('a', 'b'), alpha='0.05'):
    plan = {'schema': r.frozen.SCHEMA, 'baseline': 'base-v1',
            'candidates': list(candidates), 'pass_rule': 'Synthetic exact match.',
            'alpha': alpha, 'cases': list(cases)}
    manifest = r.frozen.freeze(r.frozen.canonical(plan))
    return r.frozen.canonical(manifest), manifest['plan_sha256']


def raw_csv(rows, candidates=('a', 'b')):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['case', 'baseline', *candidates])
    writer.writerows(rows)
    return stream.getvalue().encode()


def run_check(raw, manifest=None, pin=None, **kwargs):
    if manifest is None:
        manifest, pin = fixture()
    return r.check(manifest, raw, pin, r.digest(raw), **kwargs)


class RosterTests(unittest.TestCase):
    def test_demo_preserves_counts_and_separate_unknowns(self):
        demo = r.demo()
        out = demo['report']
        self.assertIn('omitted', demo['default_rejection'])
        self.assertEqual(out['restored_all_unknown_case_ids'], ['unicode'])
        self.assertEqual(out['restored_unknown_cell_count'], 3)
        self.assertEqual(out['supplied_unknown_cell_count'], 1)
        self.assertEqual(out['analysis']['missing_cells'], 4)
        self.assertEqual(out['analysis']['planned_cases_retained'], 3)
        self.assertEqual(out['analysis']['candidate_count'], 2)
        self.assertEqual(out['analysis']['input_sha256'], r.digest(demo['normalized_csv'].encode()))

    def test_every_case_omission_subset_and_permutation(self):
        all_rows = [('first', 0, 1, '?'), ('second', 1, 0, 1), ('third', '?', 0, 0)]
        for size in range(4):
            for subset in itertools.combinations(all_rows, size):
                for rows in itertools.permutations(subset):
                    raw = raw_csv(rows)
                    if size != 3:
                        with self.assertRaisesRegex(ValueError, 'omitted'):
                            run_check(raw)
                    out, normalized = run_check(raw, restore_omitted_cases=True)
                    actual = list(csv.reader(io.StringIO(normalized.decode())))
                    self.assertEqual([row[0] for row in actual[1:]], ['first', 'second', 'third'])
                    original = {row[0]: list(map(str, row)) for row in rows}
                    for row in actual[1:]:
                        self.assertEqual(row, original.get(row[0], [row[0], '?', '?', '?']))
                    self.assertEqual(out['restored_unknown_cell_count'], (3-size)*3)

    def test_family_drift_rejected_even_with_restoration(self):
        for names in [('a',), ('a', 'b', 'c'), ('b', 'a'), ('a', 'renamed')]:
            raw = raw_csv([['first'] + [0]*(len(names)+1)], names)
            with self.assertRaisesRegex(ValueError, 'family'):
                run_check(raw, restore_omitted_cases=True)

    def test_unplanned_duplicates_invalid_cells_and_csv(self):
        for raw in [raw_csv([('extra', 0, 1, 1)]),
                    raw_csv([('first', 0, 1, 1)]*2),
                    raw_csv([('first', 0, '', 1)]),
                    raw_csv([('first', 0, 'NA', 1)]),
                    raw_csv([('first', 0, 'true', 1)]),
                    b'case,baseline,a,b\nfirst,0,1\n',
                    b'case,baseline,a,b\n\n',
                    b'case,baseline,a,b\n"first,0,1,1\n',
                    b'case,baseline,a,b\n\xff,0,1,1\n']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                run_check(raw, restore_omitted_cases=True)

    def test_independent_pins_reject_self_consistent_plan_replacement(self):
        raw = raw_csv([('first', 0, 1, 1)])
        manifest, pin = fixture()
        forged, _ = fixture(cases=('first', 'new', 'third'))
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            r.check(forged, raw, pin, r.digest(raw), restore_omitted_cases=True)
        for wrong in ['0'*64, '', None, 'A'*64]:
            with self.assertRaises(ValueError):
                r.check(manifest, raw, pin, wrong, restore_omitted_cases=True)
        with self.assertRaises(ValueError):
            r.check(manifest, raw+b'\n', pin, r.digest(raw), restore_omitted_cases=True)

    def test_wholly_absent_data_retains_full_family(self):
        out, _ = run_check(raw_csv([]), restore_omitted_cases=True)
        self.assertEqual(out['analysis']['missing_cells'], 9)
        for candidate in out['analysis']['candidates']:
            bounds = [F(int(q['numerator']), int(q['denominator']))
                      for q in candidate['candidate_minus_baseline_bounds']]
            self.assertEqual(bounds, [-1, 1])

    def test_direct_engine_agreement_for_seeded_partial_tables(self):
        rng = random.Random(3701)
        for _ in range(25):
            rows = [(case, *(rng.choice(['0', '1', '?']) for _ in range(3)))
                    for case in ('first', 'second', 'third')]
            rng.shuffle(rows)
            raw = raw_csv(rows)
            out, normalized = run_check(raw, margin=F(1, 5))
            self.assertEqual(out['analysis'], r.missing.analyze(normalized, F(1, 20), F(1, 5)))
            self.assertFalse(out['restoration_authorized'])
            self.assertEqual(out['restored_all_unknown_case_ids'], [])

    def test_complete_data_matches_original_frozen_admission(self):
        manifest, pin = fixture()
        raw = raw_csv([('third', 1, 0, 1), ('first', 0, 1, 0), ('second', 0, 0, 1)])
        _, expected = r.frozen.check(manifest, raw, pin)
        out, actual = run_check(raw)
        self.assertEqual(actual, expected)
        self.assertEqual(out['analysis']['missing_cells'], 0)

    def test_unicode_bom_crlf_and_long_precision_alpha(self):
        manifest, pin = fixture(cases=('é,一',), candidates=('系统', 'b'), alpha='0.050000000000000001')
        raw = '\ufeffcase,baseline,系统,b\r\n"é,一",?,1,0\r\n'.encode()
        out, normalized = run_check(raw, manifest, pin)
        self.assertIn('"é,一"', normalized.decode())
        self.assertEqual(out['analysis']['familywise_alpha'],
                         {'numerator': '50000000000000001', 'denominator': '1000000000000000000'})

    def test_limits_fail_before_analysis(self):
        for cases, names in [(tuple(f'c{i}' for i in range(513)), ('a', 'b')),
                             (('x'*201,), ('a', 'b')), (('x\u200b',), ('a', 'b')),
                             (('first',), ('a'*201, 'b'))]:
            manifest, pin = fixture(cases, names)
            with self.assertRaises(ValueError):
                run_check(raw_csv([], names), manifest, pin, restore_omitted_cases=True)
        with self.assertRaises(ValueError):
            run_check(b'x'*(r.frozen.MAX_BYTES+1))
        with self.assertRaises(ValueError):
            run_check(raw_csv([]), restore_omitted_cases=1)

    def test_cli_copied_folder_pins_no_partial_output_and_containment(self):
        scratch = Path.cwd()/'test'/'scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            folder = Path(temp)
            for filename in ('roster_bounds.py', 'frozen_engine.py', 'missing_bounds.py', 'bounds_engine.py'):
                shutil.copyfile(Path(r.__file__).parent/filename, folder/filename)
            manifest, pin = fixture()
            raw = raw_csv([('first', 0, 1, '?')])
            (folder/'plan.json').write_bytes(manifest)
            (folder/'data.csv').write_bytes(raw)
            def cli(*args):
                return subprocess.run([sys.executable, '-B', 'roster_bounds.py', *args],
                                      cwd=folder, capture_output=True, timeout=30)
            args = ['check', '--manifest', 'plan.json', '--results', 'data.csv',
                    '--expected-plan-sha256', pin, '--expected-results-sha256', r.digest(raw)]
            bad = cli(*args)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, b'')
            good = cli(*args, '--restore-omitted-cases')
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(good.stdout)['restored_unknown_cell_count'], 6)
            emitted = cli(*args, '--restore-omitted-cases', '--emit-csv')
            self.assertEqual(emitted.returncode, 0, emitted.stderr)
            self.assertEqual(r.digest(emitted.stdout), json.loads(good.stdout)['normalized_csv_sha256'])
            invalid = cli(*args, '--restore-omitted-cases', '--margin', 'NaN', '--emit-csv')
            self.assertEqual(invalid.returncode, 2)
            self.assertEqual(invalid.stdout, b'')
            (folder/'escape.csv').symlink_to(folder.parent/'not-an-input.csv')
            denied = cli(*[('escape.csv' if x == 'data.csv' else x) for x in args])
            self.assertEqual(denied.returncode, 2)
            self.assertEqual(denied.stdout, b'')
            self.assertEqual((folder/'plan.json').read_bytes(), manifest)
            self.assertEqual((folder/'data.csv').read_bytes(), raw)
            self.assertEqual(cli('demo').returncode, 0)


if __name__ == '__main__':
    unittest.main()
