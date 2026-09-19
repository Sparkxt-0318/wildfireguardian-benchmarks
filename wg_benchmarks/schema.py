"""Benchmark / expected-result schema validation.

Uses ``jsonschema`` when it is installed.  When it is not — the common case for
a clean checkout, since this repository has no required third-party
dependencies — the small validator below covers the subset of JSON Schema
draft 2020-12 used by ``schemas/*.json``:

``type``, ``enum``, ``const``, ``required``, ``properties``,
``patternProperties``, ``additionalProperties``, ``items``, ``prefixItems``,
``minItems``, ``maxItems``, ``uniqueItems``, ``minimum``, ``maximum``,
``exclusiveMinimum``, ``exclusiveMaximum``, ``pattern``, ``minLength``,
``maxLength``, ``anyOf``, ``oneOf``, ``allOf``, ``not``, ``$ref`` (local
``#/$defs/...`` only).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    python_type = _TYPES.get(expected)
    if python_type is None:
        raise ValueError(f"unsupported schema type: {expected}")
    return isinstance(value, python_type)


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"only local refs are supported, got {ref!r}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _validate(value: Any, schema: dict, root: dict, path: str, errors: list[str]) -> None:
    if schema is True or schema == {}:
        return
    if schema is False:
        errors.append(f"{path}: schema forbids any value")
        return

    if "$ref" in schema:
        _validate(value, _resolve(schema["$ref"], root), root, path, errors)
        return

    if "type" in schema:
        types = schema["type"]
        types = types if isinstance(types, list) else [types]
        if not any(_type_ok(value, t) for t in types):
            errors.append(f"{path}: expected type {'/'.join(types)}, got {type(value).__name__}")
            return

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: {value!r} != const {schema['const']!r}")

    for keyword, combinator in (("allOf", all), ("anyOf", any)):
        if keyword in schema:
            outcomes = []
            for index, sub in enumerate(schema[keyword]):
                sub_errors: list[str] = []
                _validate(value, sub, root, f"{path}", sub_errors)
                outcomes.append(not sub_errors)
                if keyword == "allOf":
                    errors.extend(sub_errors)
            if keyword == "anyOf" and not combinator(outcomes):
                errors.append(f"{path}: does not match any of the {len(outcomes)} alternatives")
    if "oneOf" in schema:
        matches = 0
        for sub in schema["oneOf"]:
            sub_errors: list[str] = []
            _validate(value, sub, root, path, sub_errors)
            matches += not sub_errors
        if matches != 1:
            errors.append(f"{path}: matched {matches} oneOf alternatives, expected exactly 1")
    if "not" in schema:
        sub_errors = []
        _validate(value, schema["not"], root, path, sub_errors)
        if not sub_errors:
            errors.append(f"{path}: value must not match the 'not' schema")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        pattern_properties = schema.get("patternProperties", {})
        additional = schema.get("additionalProperties", True)
        for key, sub_value in value.items():
            sub_path = f"{path}.{key}" if path else key
            handled = False
            if key in properties:
                _validate(sub_value, properties[key], root, sub_path, errors)
                handled = True
            for pattern, sub_schema in pattern_properties.items():
                if re.search(pattern, str(key)):
                    _validate(sub_value, sub_schema, root, sub_path, errors)
                    handled = True
            if not handled:
                if additional is False:
                    errors.append(f"{sub_path}: additional property not allowed")
                elif isinstance(additional, dict):
                    _validate(sub_value, additional, root, sub_path, errors)

    if isinstance(value, list):
        prefix = schema.get("prefixItems", [])
        for index, sub_schema in enumerate(prefix):
            if index < len(value):
                _validate(value[index], sub_schema, root, f"{path}[{index}]", errors)
        if "items" in schema:
            for index in range(len(prefix), len(value)):
                _validate(value[index], schema["items"], root, f"{path}[{index}]", errors)
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: needs at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: allows at most {schema['maxItems']} items")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True, default=str) for v in value}) != len(value):
            errors.append(f"{path}: items must be unique")

    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match /{schema['pattern']}/")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        for keyword, op, text in (
            ("minimum", lambda a, b: a >= b, ">="),
            ("maximum", lambda a, b: a <= b, "<="),
            ("exclusiveMinimum", lambda a, b: a > b, ">"),
            ("exclusiveMaximum", lambda a, b: a < b, "<"),
        ):
            if keyword in schema and not op(value, schema[keyword]):
                errors.append(f"{path}: {value} must be {text} {schema[keyword]}")


def validate(instance: Any, schema: dict) -> list[str]:
    """Return a list of human-readable validation errors (empty means valid)."""
    try:  # pragma: no cover - environment dependent
        import jsonschema  # type: ignore

        validator = jsonschema.Draft202012Validator(schema)
        return [
            f"{'.'.join(str(p) for p in error.path) or '<root>'}: {error.message}"
            for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        ]
    except ImportError:
        errors: list[str] = []
        _validate(instance, schema, schema, "", errors)
        return errors


def load_schema(name: str) -> dict:
    with open(SCHEMA_DIR / name, "r", encoding="utf-8") as handle:
        return json.load(handle)
