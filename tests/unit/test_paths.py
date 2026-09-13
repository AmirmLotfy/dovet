from __future__ import annotations

from pathlib import Path

import pytest
from dovet.paths import (
    UnsafePathError,
    reject_platform_collisions,
    resolve_beneath,
    validate_relative_path,
)


@pytest.mark.parametrize(
    "path", ["../secret", "/absolute", "a/../b", "C:/windows", "a\\b", "x\x00y"]
)
def test_rejects_unsafe_relative_paths(path: str) -> None:
    with pytest.raises(UnsafePathError):
        validate_relative_path(path)


def test_rejects_symlink_escape(tmp_path: Path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "secret").write_text("no")
    (root / "link").symlink_to(outside / "secret")
    with pytest.raises(UnsafePathError):
        resolve_beneath(root, "link")


def test_rejects_case_and_unicode_collisions() -> None:
    with pytest.raises(UnsafePathError):
        reject_platform_collisions(["Readme", "README"])
    with pytest.raises(UnsafePathError):
        reject_platform_collisions(["caf\u00e9", "cafe\u0301"])
