import re
import sys


_VALID_BOUNDARY_RE = re.compile(rb'^[ -~]{1,70}$')


def _parseparam(s):
    while s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        while end > 0 and (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)
        if end < 0:
            end = len(s)
            yield s
            s = ''
        else:
            yield s[:end]
            s = s[end:]


def parse_header(line):
    """Parse a Content-type like header.
    Return the main content-type and a dictionary of options.
    """
    parts = _parseparam(';' + line)
    key = next(parts)
    pdict = {}
    for p in parts:
        i = p.find('=')
        if i >= 0:
            name = p[:i].strip().lower()
            value = p[i+1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace('\\\\', '\\').replace('\\"', '"')
            pdict[name] = value
    return key, pdict


def valid_boundary(boundary):
    if boundary is None:
        return False

    if isinstance(boundary, str):
        try:
            boundary = boundary.encode('ascii')
        except UnicodeEncodeError:
            return False

    if not isinstance(boundary, (bytes, bytearray)):
        return False

    return bool(_VALID_BOUNDARY_RE.fullmatch(boundary))
