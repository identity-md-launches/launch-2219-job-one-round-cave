#!/usr/bin/env python3
"""Review CSS-style escape candidates with exact original UTF-8 byte evidence."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import stat
import sys
import unicodedata

MAX_BYTES = 2 * 1024 * 1024
HEX = b'0123456789abcdefABCDEF'
SPACE = b' \t\n\r\f'
DEMO = br'.adm\456 n { content: "\202e "; } .\5a TO { color: red }'


def scan(data, max_details=100):
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise ValueError('input must be bytes of at most 2 MiB')
    if type(max_details) is not int or not 0 <= max_details <= 1000:
        raise ValueError('max_details must be an integer from 0 to 1000')
    data.decode('utf-8', 'strict')
    details, counts = [], Counter()
    i, previous, line, line_start = 0, 0, 1, 0
    while True:
        lo = data.find(b'\\', i)
        if lo < 0:
            break
        line += data.count(b'\n', previous, lo)
        last_lf = data.rfind(b'\n', previous, lo)
        if last_lf >= 0:
            line_start = last_lf + 1
        previous = lo
        i = lo + 1
        decoded, value, terminator = None, None, b''
        if i == len(data):
            form, kind = 'end-of-input', 'trailing-backslash'
        elif data[i] in b'\r\n\f':
            form, kind = 'newline', 'context-dependent-newline'
            i += 2 if data[i:i+2] == b'\r\n' else 1
        elif data[i] in HEX:
            form = 'hex'
            start = i
            while i < len(data) and i - start < 6 and data[i] in HEX:
                i += 1
            value = int(data[start:i], 16)
            if i < len(data) and data[i] in SPACE:
                end = i + (2 if data[i:i+2] == b'\r\n' else 1)
                terminator, i = data[i:end], end
            if value == 0 or value > 0x10ffff or 0xd800 <= value <= 0xdfff:
                decoded, kind = '\ufffd', 'replacement'
            else:
                decoded = chr(value)
                kind = 'ascii' if 0x20 <= value <= 0x7e else 'non-ascii-or-control'
        else:
            form = 'simple'
            first = data[i]
            width = 1 if first < 128 else 2 if first < 224 else 3 if first < 240 else 4
            decoded = data[i:i+width].decode('utf-8')
            i += width
            if decoded == '\0':
                decoded, kind = '\ufffd', 'replacement'
            else:
                kind = 'ascii' if 0x20 <= ord(decoded) <= 0x7e else 'non-ascii-or-control'
        counts[kind] += 1
        if len(details) < max_details:
            raw = data[lo:i]
            details.append({
                'source_byte_range': [lo, i],
                'source_line': line, 'source_byte_column': lo - line_start + 1,
                'source_escape_hex': raw.hex(),
                'source_span_sha256': hashlib.sha256(raw).hexdigest(),
                'form': form, 'kind': kind, 'written_hex_value': value,
                'consumed_whitespace_hex': terminator.hex(),
                'decoded_scalar': None if decoded is None else {
                    'codepoint': f'U+{ord(decoded):04X}',
                    'name': unicodedata.name(decoded, 'UNNAMED'),
                    'category': unicodedata.category(decoded),
                    'utf8_hex': decoded.encode('utf-8').hex(),
                },
            })
    total = sum(counts.values())
    return {
        'schema_version': 1, 'tool': 'css-unicode/1',
        'source_sha256': hashlib.sha256(data).hexdigest(), 'source_bytes': len(data),
        'unicode_version': unicodedata.unidata_version,
        'analysis_complete': True, 'escape_count': total,
        'counts_by_kind': dict(sorted(counts.items())),
        'detail_cap': max_details, 'retained_details': len(details),
        'omitted_details': total - len(details), 'details': details,
        'coverage': 'Non-overlapping CSS-style backslash candidates, including printable ASCII escapes.',
        'limitations': [
            'Lexical candidates only: no CSS tokenization, identifier validity, HTML parsing, cascade or rendering.',
            'Candidates inside comments and other non-CSS text are included; presence does not establish browser interpretation or intent.',
            'Hex escapes consume one to six digits and at most one CSS whitespace terminator (CRLF is one preprocessed newline).',
            'Escaped NUL, surrogate and out-of-range values map to U+FFFD; original bytes and written hex value remain evidence.',
            'Backslash-newline is reported without a decoded scalar: string continuation and invalid identifier escape differ by context.',
            'Trailing backslash has no decoded scalar; literal Unicode, other encodings and recursive decoding are outside scope.',
            'Ranges are zero-based half-open original UTF-8 bytes; lines and byte columns are one-based, LF-only, not CSS preprocessed coordinates.',
            'ASCII JSON protects terminal display, not HTML insertion. Hashes identify bytes, not authenticity. Zero escapes does not establish safety.',
        ],
    }


def read_selected(path):
    selected = Path(path).resolve(strict=True)
    if not selected.is_relative_to(Path.cwd().resolve()):
        raise ValueError('file must resolve within the current working directory')
    if not stat.S_ISREG(selected.stat().st_mode):
        raise ValueError('input must be a regular file')
    with selected.open('rb') as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('input exceeds 2 MiB')
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo', action='store_true')
    group.add_argument('--file', type=Path)
    parser.add_argument('--max-details', type=int, default=100)
    args = parser.parse_args(argv)
    try:
        report = scan(DEMO if args.demo else read_selected(args.file), args.max_details)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2
    report['source_kind'] = 'synthetic-demo' if args.demo else 'selected-file'
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    return 0 if args.demo or not report['escape_count'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
