import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

spec = importlib.util.spec_from_file_location('css_unicode', Path(__file__).with_name('css_unicode.py'))
css = importlib.util.module_from_spec(spec)
spec.loader.exec_module(css)


class CSSUnicodeTests(unittest.TestCase):
    def details(self, data):
        return css.scan(data)['details']

    def test_demo(self):
        ds = self.details(css.DEMO)
        self.assertEqual([d['decoded_scalar']['codepoint'] for d in ds], ['U+0456', 'U+202E', 'U+005A'])

    def test_six_digit_limit(self):
        ds = self.details(br'\000061b\000062c')
        self.assertEqual([d['source_escape_hex'] for d in ds], [br'\000061'.hex(), br'\000062'.hex()])
        self.assertEqual([d['decoded_scalar']['codepoint'] for d in ds], ['U+0061', 'U+0062'])

    def test_whitespace_terminators(self):
        for ws in [b' ', b'\t', b'\n', b'\r', b'\f', b'\r\n']:
            raw = b'\\41' + ws
            d = self.details(raw + b' extra')[0]
            self.assertEqual(d['source_byte_range'], [0, len(raw)])
            self.assertEqual(d['consumed_whitespace_hex'], ws.hex())
            self.assertEqual(d['decoded_scalar']['codepoint'], 'U+0041')

    def test_replacement(self):
        for raw in [br'\0', br'\D800', br'\dfff', br'\110000', br'\FFFFFF', b'\\\0']:
            d = self.details(raw)[0]
            self.assertEqual(d['kind'], 'replacement')
            self.assertEqual(d['decoded_scalar']['codepoint'], 'U+FFFD')

    def test_simple_nonascii(self):
        d = self.details('é\\🐸'.encode())[0]
        self.assertEqual(d['source_byte_range'], [2, 7])
        self.assertEqual(d['source_byte_column'], 3)
        self.assertEqual(d['decoded_scalar']['codepoint'], 'U+1F438')

    def test_no_recursive_decoding(self):
        ds = self.details(br'\\202e')
        self.assertEqual(len(ds), 1)
        self.assertEqual(ds[0]['decoded_scalar']['codepoint'], 'U+005C')
        self.assertEqual(ds[0]['source_byte_range'], [0, 2])

    def test_newline_context(self):
        for newline in [b'\n', b'\r', b'\r\n', b'\f']:
            ds = self.details(b'\\' + newline + br'\41')
            self.assertEqual(ds[0]['kind'], 'context-dependent-newline')
            self.assertIsNone(ds[0]['decoded_scalar'])
            self.assertEqual(ds[1]['source_line'], 2 if b'\n' in newline else 1)

    def test_eof(self):
        d = self.details(b'end\\')[0]
        self.assertEqual(d['source_byte_range'], [3, 4])
        self.assertEqual(d['kind'], 'trailing-backslash')
        self.assertIsNone(d['decoded_scalar'])

    def test_cap_counts(self):
        data = br'\61 \202e ' * 300
        report = css.scan(data, 1)
        self.assertEqual(report['escape_count'], 600)
        self.assertEqual(report['omitted_details'], 599)
        self.assertEqual(report['counts_by_kind'], {'ascii': 300, 'non-ascii-or-control': 300})
        self.assertEqual(css.scan(data, 0)['details'], [])

    def test_validation(self):
        for data in [b'\xff', b'a' * (css.MAX_BYTES + 1), 'text', bytearray(b'hi')]:
            with self.assertRaises(ValueError):
                css.scan(data)
        for cap in [-1, 1001, True, 1.5]:
            with self.assertRaises(ValueError):
                css.scan(b'', cap)
        self.assertEqual(css.scan(b'a' * css.MAX_BYTES)['escape_count'], 0)

    def test_seeded_scalar_oracle_and_evidence(self):
        rng = random.Random(38)
        for _ in range(500):
            scalar = rng.randrange(0x110000)
            if 0xd800 <= scalar <= 0xdfff or scalar == 0:
                continue
            prefix = ('é\n' * rng.randrange(5)).encode()
            escape = ('\\' + format(scalar, '06x') + ' ').encode()
            data = prefix + escape + b'after'
            report = css.scan(data)
            d = report['details'][0]
            lo, hi = d['source_byte_range']
            self.assertEqual(data[lo:hi], escape)
            self.assertEqual(d['source_span_sha256'], hashlib.sha256(escape).hexdigest())
            self.assertEqual(d['decoded_scalar']['utf8_hex'], chr(scalar).encode().hex())
            self.assertEqual(d['source_line'], prefix.count(b'\n') + 1)
            self.assertEqual(report['source_sha256'], hashlib.sha256(data).hexdigest())

    def test_ascii_output(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(css.main(['--demo']), 0)
        buf.getvalue().encode('ascii')
        self.assertEqual(json.loads(buf.getvalue())['source_kind'], 'synthetic-demo')

    def test_confined_file(self):
        with self.assertRaises(ValueError):
            css.read_selected(Path.cwd().parent)
        with self.assertRaises(ValueError):
            css.read_selected(Path.cwd())
        self.assertEqual(css.read_selected(Path(__file__)), Path(__file__).read_bytes())

    def test_cli_real_file_and_invalid(self):
        cmd = [sys.executable, '-B', str(Path(css.__file__))]
        result = subprocess.run(cmd + ['--file', str(Path(__file__))], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertGreater(json.loads(result.stdout)['escape_count'], 0)
        result = subprocess.run(cmd + ['--demo', '--max-details', '-1'], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('error', json.loads(result.stderr))


if __name__ == '__main__':
    unittest.main()
