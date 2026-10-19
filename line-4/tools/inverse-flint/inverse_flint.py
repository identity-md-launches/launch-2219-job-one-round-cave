#!/usr/bin/env python3
"""Find a unique inverse of a supplied monotone piecewise-linear table."""

import argparse
import json
import sys

from engine import Parser, Quantity, UnitError, dimensions, exact_decimal

MAX_BYTES = 65536


def parse(text, target=False):
    if not isinstance(text, str):
        raise ValueError('quantities and units must be expression strings')
    return Parser(text, target=target).parse()


def bound(value, dims):
    return Parser.bounded(Quantity(value, dims), 0).value


def calculate(request):
    required = {'schema', 'points', 'at', 'to'}
    if (not isinstance(request, dict) or not required <= request.keys()
            or request.keys() - required - {'expect', 'extrapolate'}):
        raise ValueError('request requires schema, points, at, to; optional expect, extrapolate')
    if request['schema'] != 'inverse-flint/1':
        raise ValueError('unsupported schema')
    allow = request.get('extrapolate', False)
    if type(allow) is not bool:
        raise ValueError('extrapolate must be boolean')
    points = request['points']
    if not isinstance(points, list) or not 2 <= len(points) <= 128:
        raise ValueError('points must contain 2..128 entries')
    parsed = []
    direction = 0
    for point in points:
        if not isinstance(point, dict) or set(point) != {'x', 'y'}:
            raise ValueError('each point requires exactly x and y')
        x, y = parse(point['x']), parse(point['y'])
        if parsed:
            if x.dims != parsed[0][0].dims or y.dims != parsed[0][1].dims:
                raise ValueError('all x dimensions and all y dimensions must agree')
            if x.value <= parsed[-1][0].value:
                raise ValueError('x coordinates must be strictly increasing')
            change = (y.value > parsed[-1][1].value) - (y.value < parsed[-1][1].value)
            if change:
                if direction and change != direction:
                    raise ValueError('y values must be monotone')
                direction = change
        parsed.append((x, y))
    if not direction:
        raise ValueError('a constant table has no unique inverse')
    query, target = parse(request['at']), parse(request['to'], target=True)
    xd, yd = parsed[0][0].dims, parsed[0][1].dims
    if query.dims != yd:
        raise ValueError('query dimensions do not match y')
    if target.dims != xd or target.value <= 0:
        raise ValueError('target must have x dimensions and a positive scale')
    low = min(parsed[0][1].value, parsed[-1][1].value)
    high = max(parsed[0][1].value, parsed[-1][1].value)
    outside = query.value < low or query.value > high
    if outside and not allow:
        raise ValueError('query outside table; explicit extrapolate=true required')
    # Any plateau at the queried reading contains infinitely many x values.
    for i in range(len(parsed) - 1):
        if parsed[i][1].value == parsed[i + 1][1].value == query.value:
            raise ValueError('query lies on a flat segment; inverse is not unique')
    candidates = [i for i in range(len(parsed) - 1)
                  if parsed[i][1].value != parsed[i + 1][1].value
                  and min(parsed[i][1].value, parsed[i + 1][1].value) <= query.value
                  <= max(parsed[i][1].value, parsed[i + 1][1].value)]
    if candidates:
        i = candidates[-1]  # At a shared knot, use the segment to its right.
    else:
        before_first = (query.value < low) if direction > 0 else (query.value > high)
        i = 0 if before_first else len(parsed) - 2
        if parsed[i][1].value == parsed[i + 1][1].value:
            raise ValueError('cannot extrapolate through a flat boundary segment')
    (x0, y0), (x1, y1) = parsed[i:i + 2]
    dx = bound(x1.value - x0.value, xd)
    dy = bound(y1.value - y0.value, yd)
    offset = bound(query.value - y0.value, yd)
    weight = bound(offset / dy, (0, 0, 0, 0))
    value = bound(x0.value + bound(weight * dx, xd), xd)
    inverse_slope_dims = tuple(a - b for a, b in zip(xd, yd))
    inverse_slope = bound(dx / dy, inverse_slope_dims)
    shown = bound(value / target.value, xd)
    result = {
        'schema': 'inverse-flint-result/1', 'method': 'inverse-piecewise-linear',
        'extrapolated': outside, 'at': request['at'],
        'segment': {'left_index': i, 'right_index': i + 1,
                    'left': points[i], 'right': points[i + 1],
                    'right_weight': exact_decimal(weight),
                    'inverse_slope_base_value': exact_decimal(inverse_slope),
                    'inverse_slope_base_unit': dimensions(inverse_slope_dims)},
        'value': exact_decimal(shown), 'unit': request['to'],
        'base_value': exact_decimal(value), 'base_unit': dimensions(xd),
        'passes': True,
    }
    if 'expect' in request:
        expected = parse(request['expect'])
        if expected.dims != xd:
            raise ValueError('expected dimensions do not match x')
        difference = bound(value - expected.value, xd)
        result['check'] = {'expression': request['expect'], 'matches': difference == 0,
                           'difference_base_value': exact_decimal(difference)}
        result['passes'] = difference == 0
    return result


def reject(value):
    raise ValueError('JSON numeric values are unsupported; use expression strings')


def unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def load(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('input exceeds 65536 bytes')
    text = raw.decode('utf-8')
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            if depth > 4:
                raise ValueError('JSON nesting exceeds four levels')
        elif char in ']}':
            depth -= 1
    return json.loads(text, object_pairs_hook=unique, parse_int=reject,
                      parse_float=reject, parse_constant=reject)


def example():
    return {'schema': 'inverse-flint/1',
            'points': [{'x': '0 g', 'y': '0 mm'}, {'x': '500 g', 'y': '2 mm'},
                       {'x': '1 kg', 'y': '5 mm'}],
            'at': '3.5 mm', 'to': 'g', 'expect': '750 g'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'demo'])
    args = parser.parse_args(argv)
    try:
        request = example() if args.command == 'demo' else load(sys.stdin.buffer.read(MAX_BYTES + 1))
        result = calculate(request)
    except (ValueError, TypeError, UnicodeError, UnitError, OverflowError, ZeroDivisionError) as exc:
        print('inverse-flint: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result['passes'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
