"""Content-addressed, atomically published local artifacts."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .canonical import sha256_bytes
from .paths import private_directory


@dataclass(frozen=True)
class StoredArtifact:
    sha256: str
    size_bytes: int
    path: Path


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = private_directory(root)
        self.objects = private_directory(root / "objects" / "sha256")
        self.staging = private_directory(root / "staging")

    def object_path(self, digest: str) -> Path:
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("invalid SHA-256 digest")
        return self.objects / digest[:2] / digest

    def put_bytes(self, data: bytes) -> StoredArtifact:
        digest = sha256_bytes(data)
        target = self.object_path(digest)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if target.exists():
            self._verify(target, digest, len(data))
            return StoredArtifact(digest, len(data), target)

        descriptor, temporary = tempfile.mkstemp(prefix="object-", dir=self.staging)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary, 0o600)
            try:
                os.link(temporary, target)
            except FileExistsError:
                pass
            self._fsync_directory(target.parent)
            self._verify(target, digest, len(data))
        finally:
            Path(temporary).unlink(missing_ok=True)
        return StoredArtifact(digest, len(data), target)

    def read_bytes(self, digest: str) -> bytes:
        path = self.object_path(digest)
        data = path.read_bytes()
        self._verify(path, digest, len(data))
        return data

    @staticmethod
    def _verify(path: Path, expected_digest: str, expected_size: int) -> None:
        data = path.read_bytes()
        if len(data) != expected_size or sha256_bytes(data) != expected_digest:
            raise OSError(f"artifact integrity check failed: {path}")

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
