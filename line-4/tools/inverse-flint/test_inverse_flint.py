"""Independent arithmetic and command-line checks for inverse calibration."""

from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from inverse_flint import calculate, example, load

SCRIPT = Path(__file__).with_name('inverse_flint.py')


class InverseFlintTests(unittest.TestCase):
    def test_demo_and_claim(self):
        result = calculate(example())
        self.assertEqual(result['value'], '750')
        self.assertEqual(result['unit'], 'g')
        self.assertEqual(result['segment']['right_weight'], '0.5')
        self.assertTrue(result['passes'])

    def test_seeded_fraction_oracle_increasing_and_decreasing(self):
        rng = random.Random(36)
        for sign in (1, -1):
            for _ in range(200):
                x0 = rng.randrange(-30, 30)
                width = rng.randrange(1, 30)
                y0 = rng.randrange(-30, 30)
                rise = rng.randrange(1, 30) * sign
                numerator = rng.randrange(0, 31)
                fraction = Fraction(numerator, 30)
                y_query = Fraction(y0) + fraction * rise
                request = {'schema': 'inverse-flint/1',
                           'points': [{'x': f'{x0} m', 'y': f'{y0} s'},
                                      {'x': f'{x0 + width} m', 'y': f'{y0 + rise} s'}],
                           'at': f'({y_query}) * s', 'to': 'm'}
                result = calculate(request)
                shown = Fraction(result['value'])
                self.assertEqual(shown, Fraction(x0) + fraction * width)
                self.assertEqual(Fraction(result['segment']['inverse_slope_base_value']),
                                 Fraction(width, rise))

    def test_plateau_rejected_only_at_its_reading(self):
        request = {'schema': 'inverse-flint/1',
                   'points': [{'x': '0 s', 'y': '0 m'}, {'x': '1 s', 'y': '1 m'},
                              {'x': '2 s', 'y': '1 m'}, {'x': '3 s', 'y': '3 m'}],
                   'at': '1 m', 'to': 's'}
        with self.assertRaisesRegex(ValueError, 'not unique'):
            calculate(request)
        request['at'] = '2 m'
        self.assertEqual(calculate(request)['value'], '2.5')

    def test_knot_uses_right_segment(self):
        request = example()
        request['at'] = '2 mm'
        request['expect'] = '500 g'
        self.assertEqual(calculate(request)['segment']['left_index'], 1)

    def test_extrapolation_requires_flag(self):
        request = example()
        request['at'] = '8 mm'
        with self.assertRaisesRegex(ValueError, 'extrapolate'):
            calculate(request)
        request['extrapolate'] = True
        request['expect'] = '1500 g'
        result = calculate(request)
        self.assertTrue(result['extrapolated'])
        self.assertTrue(result['passes'])
        self.assertEqual(result['segment']['left_index'], 1)

    def test_flat_boundary_cannot_be_extrapolated(self):
        request = {'schema': 'inverse-flint/1',
                   'points': [{'x': '0 s', 'y': '0 m'}, {'x': '1 s', 'y': '0 m'},
                              {'x': '2 s', 'y': '1 m'}],
                   'at': '-0.1 m', 'to': 's', 'extrapolate': True}
        with self.assertRaisesRegex(ValueError, 'flat boundary'):
            calculate(request)
        request['points'] = [{'x': '0 s', 'y': '0 m'}, {'x': '1 s', 'y': '1 m'},
                             {'x': '2 s', 'y': '1 m'}]
        request['at'] = '1.1 m'
        with self.assertRaisesRegex(ValueError, 'flat boundary'):
            calculate(request)

    def test_mixed_units_and_failed_claim(self):
        request = example()
        request['to'] = 'kg'
        request['expect'] = '700 g'
        result = calculate(request)
        self.assertEqual(result['value'], '0.75')
        self.assertEqual(result['check']['difference_base_value'], '0.05')
        self.assertFalse(result['passes'])

    def test_invalid_tables_and_types(self):
        request = example()
        request['points'][2]['y'] = '1 mm'
        with self.assertRaisesRegex(ValueError, 'monotone'):
            calculate(request)
        request = example()
        request['points'][2]['x'] = '500 g'
        with self.assertRaisesRegex(ValueError, 'strictly increasing'):
            calculate(request)
        request = example()
        request['points'][1]['y'] = '2 s'
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            calculate(request)
        request = example()
        request['extrapolate'] = 1
        with self.assertRaisesRegex(ValueError, 'boolean'):
            calculate(request)
        request = example()
        request['points'] = request['points'][:2]
        request['points'][1]['y'] = '0 mm'
        with self.assertRaisesRegex(ValueError, 'constant'):
            calculate(request)

    def test_json_limits_and_duplicate_keys(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            load(b'{"schema":"inverse-flint/1","schema":"inverse-flint/1"}')
        with self.assertRaisesRegex(ValueError, 'numeric'):
            load(b'{"at":1}')
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            load(b' ' * 65537)

    def test_cli_statuses(self):
        def run(args, data=b''):
            return subprocess.run([sys.executable, '-B', str(SCRIPT), *args],
                                  input=data, capture_output=True, check=False)
        demo = run(['demo'])
        self.assertEqual(demo.returncode, 0, demo.stderr)
        self.assertEqual(json.loads(demo.stdout)['value'], '750')
        failed = example()
        failed['expect'] = '1 kg'
        mismatch = run(['run'], json.dumps(failed).encode())
        self.assertEqual(mismatch.returncode, 1, mismatch.stderr)
        self.assertFalse(json.loads(mismatch.stdout)['passes'])
        bad = example()
        bad['points'][2]['y'] = '-2 mm'
        invalid = run(['run'], json.dumps(bad).encode())
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, b'')


if __name__ == '__main__':
    unittest.main()
