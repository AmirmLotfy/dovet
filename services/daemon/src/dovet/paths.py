"""Filesystem containment and manifest path checks."""

from __future__ import annotations

import os
import unicodedata
from pathlib import Path, PurePosixPath


class UnsafePathError(ValueError):
    pass


def validate_relative_path(raw: str) -> str:
    if not raw or "\x00" in raw or "\\" in raw:
        raise UnsafePathError("path must be a non-empty POSIX relative path")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise UnsafePathError("path escapes the approved root")
    if path.parts[0].endswith(":"):
        raise UnsafePathError("drive-prefixed paths are not accepted")
    return path.as_posix()


def resolve_beneath(root: Path, relative: str, *, allow_missing: bool = False) -> Path:
    clean = validate_relative_path(relative)
    root_real = root.resolve(strict=True)
    candidate = root_real.joinpath(*PurePosixPath(clean).parts)
    parent = candidate.parent.resolve(strict=True)
    if not parent.is_relative_to(root_real):
        raise UnsafePathError("resolved parent escapes the approved root")
    if candidate.exists() or candidate.is_symlink():
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(root_real):
            raise UnsafePathError("resolved path escapes the approved root")
        if candidate.is_symlink():
            raise UnsafePathError("symlink files are not supported in checkpoints")
        return resolved
    if not allow_missing:
        raise FileNotFoundError(candidate)
    return candidate


def reject_platform_collisions(paths: list[str]) -> None:
    seen: dict[str, str] = {}
    for path in paths:
        normalized = unicodedata.normalize("NFC", path).casefold()
        previous = seen.get(normalized)
        if previous is not None and previous != path:
            raise UnsafePathError(f"platform-colliding paths: {previous!r} and {path!r}")
        seen[normalized] = path


def private_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)
    return path
