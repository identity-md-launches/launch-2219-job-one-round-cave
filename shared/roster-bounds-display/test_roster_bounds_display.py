"""Cross-line contract checks, including offline copied-folder handoff."""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import roster_bounds_display as app


def fixture():
    plan = {'schema': app.frozen.SCHEMA, 'baseline': 'base',
        'candidates': ['a', 'b'], 'pass_rule': 'Exact synthetic fixture match',
        'alpha': '0.050000000000000001', 'cases': ['first', 'second', 'third']}
    frozen = app.frozen.freeze(app.frozen.canonical(plan))
    return app.frozen.canonical(frozen), frozen['plan_sha256']


def summarize(raw, **kw):
    manifest, pin = fixture()
    return app.summarize(manifest, raw, pin, app.roster.digest(raw), **kw)


class RosterDisplayTests(unittest.TestCase):
    def test_demo_keeps_roster_unknowns_and_separate_domains(self):
        result = app.demo()
        evidence, view = result['roster_evidence'], result['reading_view']
        self.assertEqual(evidence['analysis'], view['analysis'])
        self.assertEqual(evidence['restored_all_unknown_case_ids'], ['unicode'])
        self.assertEqual(evidence['restored_unknown_cell_count'], 3)
        self.assertEqual(evidence['supplied_unknown_cell_count'], 1)
        self.assertEqual(evidence['analysis']['missing_cells'], 4)
        self.assertEqual(evidence['normalized_csv_sha256'], view['input_sha256'])
        self.assertNotEqual(evidence['observation_bytes_sha256'], view['input_sha256'])
        self.assertIn('unicode,?,?,?\n', result['normalized_csv'])
        self.assertIn('omitted', result['default_omission_rejection'])

    def test_every_omission_subset_keeps_whole_family_and_encloses_completions(self):
        rows = [b'first,0,1,?\n', b'second,1,0,1\n', b'third,0,1,1\n']
        for included in itertools.product((False, True), repeat=3):
            raw = b'case,baseline,a,b\n'+b''.join(row for row, keep in zip(rows,included) if keep)
            if not all(included):
                with self.assertRaises(ValueError): summarize(raw)
            result = summarize(raw, restore_omitted_cases=True)
            original = result['roster_evidence']['analysis']
            self.assertEqual(original['planned_cases_retained'], 3)
            self.assertEqual(original['candidate_count'], 2)
            # Fill the remaining unknowns two very different ways. Every
            # completion's population interval must stay inside displayed bounds.
            for fill in (b'0', b'1'):
                complete = app.display.bounds.analyze(result['normalized_csv'].encode().replace(b'?',fill),
                    F('0.050000000000000001'))
                for shown, exact in zip(result['reading_view']['candidates'], complete['candidates']):
                    lo, hi = map(app.display.rational, exact['candidate_minus_baseline_bounds'])
                    outer = shown['population_confidence_percentage_points']
                    self.assertLessEqual(F(outer['lower'])/100,lo)
                    self.assertGreaterEqual(F(outer['upper'])/100,hi)

    def test_full_precision_alpha_and_original_analysis_unchanged(self):
        raw=b'case,baseline,a,b\nthird,1,1,0\nsecond,0,1,?\nfirst,1,0,1\n'
        result=summarize(raw)
        manifest,pin=fixture()
        original,normalized=app.roster.check(manifest,raw,pin,app.roster.digest(raw))
        self.assertEqual(result['roster_evidence'],original)
        self.assertEqual(result['normalized_csv'].encode(),normalized)
        self.assertEqual(original['analysis']['familywise_alpha'], app.display.bounds.fraction(F('0.050000000000000001')))

    def test_no_display_precision_gains_an_exact_decision(self):
        for places in range(7):
            result=summarize(b'case,baseline,a,b\nfirst,0,1,?\n',restore_omitted_cases=True,places=places)
            for row in result['reading_view']['candidates']:
                for key,value in row['displayed_interval_criteria'].items():
                    self.assertFalse(value and not row['exact_criteria'][key])
        for places in (True,-1,7,1.0):
            with self.assertRaises(ValueError):
                summarize(b'case,baseline,a,b\n',restore_omitted_cases=True,places=places)

    def test_pin_family_and_authorization_failures_are_not_hidden(self):
        manifest,pin=fixture();raw=b'case,baseline,a,b\nfirst,0,1,?\n'
        for plan_pin,result_pin in [('f'*64,app.roster.digest(raw)),(pin,'f'*64)]:
            with self.assertRaises(ValueError): app.summarize(manifest,raw,plan_pin,result_pin,restore_omitted_cases=True)
        for bad in (b'case,baseline,a\nfirst,0,1\n',b'case,baseline,b,a\nfirst,0,1,1\n',
                    raw+b'first,0,1,0\n',b'case,baseline,a,b\nother,0,1,1\n'):
            with self.assertRaises(ValueError): summarize(bad,restore_omitted_cases=True)
        with self.assertRaises(ValueError): summarize(raw,restore_omitted_cases=1)

    def test_provenance_matches_sources(self):
        here=Path(app.__file__).parent
        for entry in json.loads((here/'provenance.json').read_text()):
            data=(here/entry['copy']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(),entry['sha256'])

    def test_portable_cli_pins_fail_closed_without_partial_output(self):
        scratch=Path('test/scratch').resolve();scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            folder=Path(tmp)/'portable'
            shutil.copytree(Path(app.__file__).parent,folder,ignore=shutil.ignore_patterns('__pycache__'))
            manifest,pin=fixture();raw=b'case,baseline,a,b\nfirst,0,1,?\n'
            (folder/'plan.json').write_bytes(manifest);(folder/'results.csv').write_bytes(raw)
            command=[sys.executable,'-B','roster_bounds_display.py']
            def run(args): return subprocess.run(command+args,cwd=folder,capture_output=True,timeout=30)
            demo=run(['demo']);self.assertEqual(demo.returncode,0,demo.stderr)
            self.assertTrue(all(c<128 for c in demo.stdout))
            args=['check','--manifest','plan.json','--results','results.csv','--expected-plan-sha256',pin,
                  '--expected-results-sha256',app.roster.digest(raw)]
            rejected=run(args);self.assertEqual(rejected.returncode,2);self.assertEqual(rejected.stdout,b'')
            good=run(args+['--restore-omitted-cases']);self.assertEqual(good.returncode,0,good.stderr)
            self.assertEqual(json.loads(good.stdout)['roster_evidence']['planned_case_order'],['first','second','third'])
            (folder/'results.csv').write_bytes(raw+b'\n')
            bad=run(args+['--restore-omitted-cases']);self.assertEqual(bad.returncode,2);self.assertEqual(bad.stdout,b'')
            self.assertEqual((folder/'plan.json').read_bytes(),manifest)

if __name__=='__main__': unittest.main()
