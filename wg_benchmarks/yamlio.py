"""YAML input/output for the benchmark suite.

The suite is deliberately runnable with **zero third-party dependencies**.  If
PyYAML is installed it is used (it is faster and handles every edge case); if it
is not, the small hand-written parser below handles the restricted YAML subset
that every file in ``benchmarks/`` is written in:

* block mappings and block sequences, arbitrarily nested;
* flow sequences ``[a, b]`` and flow mappings ``{a: 1}`` (no nesting of flow
  collections beyond one level, which we never use);
* scalars: ``int``, ``float``, ``true/false``, ``null``/``~``, quoted and plain
  strings;
* ``#`` comments and blank lines.

Dumping is always done by our own writer so that regenerating a benchmark file
produces a byte-stable diff regardless of which YAML library is installed.
"""

from __future__ import annotations

import re
from typing import Any

try:  # pragma: no cover - environment dependent
    import yaml as _pyyaml
except Exception:  # pragma: no cover
    _pyyaml = None


# --------------------------------------------------------------------------
# scalars
# --------------------------------------------------------------------------

_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")


def parse_scalar(text: str) -> Any:
    """Parse a single YAML scalar token."""
    t = text.strip()
    if t == "" or t in ("null", "~", "Null", "NULL"):
        return None
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        return t[1:-1]
    low = t.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in (".inf", "+.inf"):
        return float("inf")
    if low == "-.inf":
        return float("-inf")
    if _INT_RE.match(t):
        return int(t)
    if _FLOAT_RE.match(t):
        return float(t)
    return t


def _strip_comment(line: str) -> str:
    """Remove a trailing ``#`` comment that is not inside quotes."""
    out = []
    quote = None
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out)


def _split_flow(body: str) -> list[str]:
    """Split ``a, b, {c: 1}`` on top-level commas."""
    parts, depth, quote, cur = [], 0, None, []
    for ch in body:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            cur.append(ch)
        elif ch in "[{":
            depth += 1
            cur.append(ch)
        elif ch in "]}":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        parts.append("".join(cur))
    return [p.strip() for p in parts]


def parse_value(text: str) -> Any:
    """Parse a scalar or a one-line flow collection."""
    t = text.strip()
    if t.startswith("[") and t.endswith("]"):
        return [parse_value(p) for p in _split_flow(t[1:-1])]
    if t.startswith("{") and t.endswith("}"):
        out: dict[str, Any] = {}
        for p in _split_flow(t[1:-1]):
            if not p:
                continue
            k, _, v = p.partition(":")
            out[str(parse_scalar(k))] = parse_value(v)
        return out
    return parse_scalar(t)


# --------------------------------------------------------------------------
# fallback block parser
# --------------------------------------------------------------------------


def _tokenize(text: str) -> list[tuple[int, str]]:
    lines = []
    for raw in text.splitlines():
        if raw.strip().startswith("#"):
            continue
        stripped = _strip_comment(raw).rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))
    return lines


def _parse_block(lines: list[tuple[int, str]], pos: int, indent: int) -> tuple[Any, int]:
    if pos >= len(lines):
        return None, pos
    if lines[pos][1].startswith("- "):
        return _parse_seq(lines, pos, indent)
    return _parse_map(lines, pos, indent)


def _parse_seq(lines: list[tuple[int, str]], pos: int, indent: int) -> tuple[list, int]:
    items: list[Any] = []
    while pos < len(lines):
        ind, content = lines[pos]
        if ind < indent or not (content == "-" or content.startswith("- ")):
            break
        body = content[2:].strip() if content.startswith("- ") else ""
        pos += 1
        if body == "":
            if pos < len(lines) and lines[pos][0] > ind:
                value, pos = _parse_block(lines, pos, lines[pos][0])
            else:
                value = None
            items.append(value)
            continue
        if body.startswith("- "):
            inner_indent = ind + 2
            synthetic: list[tuple[int, str]] = [(inner_indent, body)]
            while pos < len(lines) and lines[pos][0] >= inner_indent:
                synthetic.append(lines[pos])
                pos += 1
            value, _ = _parse_seq(synthetic, 0, inner_indent)
            items.append(value)
            continue
        if ":" in body and not body.startswith(("[", "{", '"', "'")):
            key, _, rest = body.partition(":")
            inner_indent = ind + 2
            synthetic: list[tuple[int, str]] = [(inner_indent, body)]
            while pos < len(lines) and lines[pos][0] >= inner_indent:
                synthetic.append(lines[pos])
                pos += 1
            value, _ = _parse_map(synthetic, 0, inner_indent)
            items.append(value)
            continue
        items.append(parse_value(body))
    return items, pos


def _parse_map(lines: list[tuple[int, str]], pos: int, indent: int) -> tuple[dict, int]:
    out: dict[str, Any] = {}
    while pos < len(lines):
        ind, content = lines[pos]
        if ind < indent:
            break
        if ind > indent:  # defensive: unexpected deeper line
            break
        if content.startswith("- "):
            break
        key, _, rest = content.partition(":")
        key = str(parse_scalar(key))
        rest = rest.strip()
        pos += 1
        if rest in ("|", "|-", ">", ">-"):
            block_lines = []
            while pos < len(lines) and lines[pos][0] > ind:
                block_lines.append(lines[pos][1])
                pos += 1
            joiner = "\n" if rest.startswith("|") else " "
            out[key] = joiner.join(block_lines)
            continue
        if rest != "":
            out[key] = parse_value(rest)
            continue
        if pos < len(lines) and lines[pos][0] > ind:
            value, pos = _parse_block(lines, pos, lines[pos][0])
            out[key] = value
        elif pos < len(lines) and lines[pos][0] == ind and lines[pos][1].startswith("- "):
            value, pos = _parse_seq(lines, pos, ind)
            out[key] = value
        else:
            out[key] = None
    return out, pos


def loads(text: str) -> Any:
    """Parse a YAML document."""
    if _pyyaml is not None:
        return _pyyaml.safe_load(text)
    lines = _tokenize(text)
    if not lines:
        return None
    value, _ = _parse_block(lines, 0, lines[0][0])
    return value


def load(path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return loads(handle.read())


# --------------------------------------------------------------------------
# dumping (always ours, for byte-stable regeneration)
# --------------------------------------------------------------------------

_PLAIN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-/ ]*$")


def _fmt_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != value:  # NaN
            return ".nan"
        if value == float("inf"):
            return ".inf"
        if value == float("-inf"):
            return "-.inf"
        if value == int(value) and abs(value) < 1e15:
            return f"{value:.1f}"
        text = repr(value)
        if "e" in text and "." not in text.split("e")[0]:
            # PyYAML's float resolver requires a decimal point before the
            # exponent: 1e-06 would otherwise be read back as a string.
            mantissa, _, exponent = text.partition("e")
            text = f"{mantissa}.0e{exponent}"
        return text
    text = str(value)
    reserved = text.lower() in ("true", "false", "null", "yes", "no", "~", "")
    if reserved or not _PLAIN_RE.match(text) or text != text.strip():
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def _fmt_key(key: Any) -> str:
    """Format a mapping key, quoting it when it would round-trip as a non-string.

    Result documents legitimately key on numeric-looking strings (a pickup
    duration of "10" minutes, for example). Writing that bare would make the
    loader hand back the integer 10 and silently break the comparison.
    """
    text = str(key)
    if isinstance(key, str) and not isinstance(parse_scalar(text), str):
        return '"' + text + '"'
    return _fmt_scalar(key)


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (bool, int, float, str))


def dumps(data: Any, indent: int = 0) -> str:
    pad = " " * indent
    lines: list[str] = []
    if isinstance(data, dict):
        if not data:
            return pad + "{}\n"
        for key, value in data.items():
            if _is_scalar(value):
                lines.append(f"{pad}{_fmt_key(key)}: {_fmt_scalar(value)}")
            elif isinstance(value, (dict, list)) and not value:
                lines.append(f"{pad}{_fmt_key(key)}: " + ("{}" if isinstance(value, dict) else "[]"))
            elif isinstance(value, list) and all(_is_scalar(v) for v in value):
                inline = ", ".join(_fmt_scalar(v) for v in value)
                if len(inline) <= 72:
                    lines.append(f"{pad}{_fmt_key(key)}: [{inline}]")
                else:
                    lines.append(f"{pad}{_fmt_key(key)}:")
                    lines.extend(f"{pad}  - {_fmt_scalar(v)}" for v in value)
            else:
                lines.append(f"{pad}{_fmt_key(key)}:")
                lines.append(dumps(value, indent + 2).rstrip("\n"))
        return "\n".join(lines) + "\n"
    if isinstance(data, list):
        if not data:
            return pad + "[]\n"
        for item in data:
            if _is_scalar(item):
                lines.append(f"{pad}- {_fmt_scalar(item)}")
            elif isinstance(item, list) and item and all(_is_scalar(v) for v in item):
                lines.append(f"{pad}- [" + ", ".join(_fmt_scalar(v) for v in item) + "]")
            elif isinstance(item, (dict, list)) and not item:
                lines.append(f"{pad}- " + ("{}" if isinstance(item, dict) else "[]"))
            else:
                body = dumps(item, indent + 2).rstrip("\n").split("\n")
                body[0] = pad + "- " + body[0][indent + 2:]
                lines.extend(body)
        return "\n".join(lines) + "\n"
    return pad + _fmt_scalar(data) + "\n"


def dump(data: Any, path) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(dumps(data))
