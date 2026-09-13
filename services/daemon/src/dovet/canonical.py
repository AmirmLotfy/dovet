"""Canonical serialization and content digests used by every trust boundary."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any


class CanonicalValueError(ValueError):
    """Raised when a value cannot participate in a Dovet digest."""


def _validate(value: Any) -> None:
    if isinstance(value, float):
        raise CanonicalValueError("floating-point values are not allowed in digest inputs")
    if value is None or isinstance(value, (str, int, bool)):
        return
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise CanonicalValueError("object keys must be strings")
        for child in value.values():
            _validate(child)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            _validate(child)
        return
    raise CanonicalValueError(f"unsupported canonical value: {type(value).__name__}")


def canonical_json(value: Any) -> bytes:
    """Encode a Dovet canonical-json/v1 value as UTF-8 bytes."""

    _validate(value)
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value))
