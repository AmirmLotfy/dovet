from __future__ import annotations

import pytest
from dovet.canonical import CanonicalValueError, canonical_json, digest_json


def test_canonical_json_vector() -> None:
    assert canonical_json({"z": "é", "a": [True, 2]}) == b'{"a":[true,2],"z":"\\u00e9"}'
    assert (
        digest_json({"a": 1}) == "015abd7f5cc57a2dd94b7590f04ad8084273905ee33ec5cebeae62276a97f862"
    )


def test_canonical_json_rejects_float() -> None:
    with pytest.raises(CanonicalValueError):
        canonical_json({"money": 0.1})
