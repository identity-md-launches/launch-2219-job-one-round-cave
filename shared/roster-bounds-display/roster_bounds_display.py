#!/usr/bin/env python3
"""Retain a pinned benchmark roster, then display incomplete bounds outward."""
import argparse
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import sys

import missing_bounds_display as display

HERE = Path(__file__).resolve().parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE/'engines'/filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

frozen = load('roster_display_frozen', 'frozen_engine.py')
# Keep the upstream imports local to this load; do not replace caller modules.
saved = {name: sys.modules.get(name) for name in ('frozen_engine', 'missing_bounds')}
sys.modules.update(frozen_engine=frozen, missing_bounds=display.missing)
try:
    roster = load('roster_display_roster', 'roster_bounds.py')
finally:
    for name, module in saved.items():
        if module is None:
            del sys.modules[name]
        else:
            sys.modules[name] = module


def summarize(manifest, observations, plan_pin, results_pin, margin=F(1,10),
              restore_omitted_cases=False, places=2):
    display.display_interval(F(0), F(0), places)
    evidence, normalized = roster.check(manifest, observations, plan_pin,
        results_pin, margin, restore_omitted_cases)
    view = display.summarize(normalized, evidence['normalized_csv_sha256'],
        F(frozen.verify_manifest(manifest, plan_pin)['alpha']),
        margin, places)
    if evidence['analysis'] != view['analysis']:
        raise ValueError('roster and display analysis disagree')
    return {'schema': 'roster-bounds-display/1', 'roster_evidence': evidence,
            'normalized_csv': normalized.decode('utf-8'), 'reading_view': view,
            'limits': [
                'Retain the plan pin before outcomes and the raw results pin independently.',
                'The legacy plan does not bind margin, display precision, case payloads or system bytes.',
                'Restoration requires explicit authorization and creates unknowns, never measured outcomes.',
                'The reading view pin identifies normalized CSV; roster evidence separately pins original observations.',
                'Both original rational intervals and outward decimal views are retained.',
                'Fixed-sample latent iid, prospective-family and honest-scoring assumptions still apply; no optional stopping.',
            ]}


def demo():
    source = roster.demo()
    example = source['report']
    # Reconstruct the documented synthetic inputs, never pretend these are live data.
    plan = {'schema': frozen.SCHEMA, 'baseline': 'synthetic-base-v1',
        'candidates': ['synthetic-a-v1', 'synthetic-b-v1'],
        'pass_rule': 'Synthetic fixture only: exact expected answer.',
        'alpha': '0.05', 'cases': ['empty', 'unicode', 'truncated']}
    manifest = frozen.canonical(frozen.freeze(frozen.canonical(plan)))
    raw = b'case,baseline,synthetic-a-v1,synthetic-b-v1\ntruncated,0,1,?\nempty,1,1,1\n'
    result = summarize(manifest, raw, example['plan_sha256'], roster.digest(raw),
                       restore_omitted_cases=True)
    result['data_kind'] = 'synthetic_demonstration'
    result['default_omission_rejection'] = source['default_rejection']
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo')
    run = sub.add_parser('check')
    run.add_argument('--manifest', required=True)
    run.add_argument('--results', required=True)
    run.add_argument('--expected-plan-sha256', required=True)
    run.add_argument('--expected-results-sha256', required=True)
    run.add_argument('--margin', default='0.1')
    run.add_argument('--places', type=int, default=2)
    run.add_argument('--restore-omitted-cases', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            margin = display.bounds.decimal(args.margin, 'margin', F(0), F(1))
            result = summarize(frozen.read_workspace(args.manifest),
                frozen.read_workspace(args.results), args.expected_plan_sha256,
                args.expected_results_sha256, margin, args.restore_omitted_cases, args.places)
            result['data_kind'] = 'user_supplied_benchmark'
        rendered = json.dumps(result, ensure_ascii=True, allow_nan=False, indent=2)+'\n'
    except (ValueError, TypeError, OSError, OverflowError, RecursionError) as exc:
        parser.exit(2, 'roster-bounds-display: '+ascii(str(exc))[:240]+'\n')
    sys.stdout.write(rendered)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
