"""Portable checkpoint bundles with strict, fail-closed import validation."""

from __future__ import annotations

import os
import stat
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from pydantic import ValidationError

from .artifacts import ArtifactStore
from .canonical import canonical_json, digest_json, sha256_bytes
from .checkpoints import CheckpointEngine
from .models import Checkpoint

MAX_BUNDLE_BYTES = 250_000_000
MAX_METADATA_BYTES = 1_000_000
MAX_MEMBERS = 5_002


class InvalidCheckpointBundle(ValueError):
    """The archive cannot be trusted as a Dovet checkpoint bundle."""


@dataclass(frozen=True)
class BundleInspection:
    checkpoint: Checkpoint
    bundle_sha256: str
    object_count: int
    total_object_bytes: int


def _archive_entry(name: str, data: bytes) -> tuple[zipfile.ZipInfo, bytes]:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o600) << 16
    return info, data


def export_bundle(checkpoint: Checkpoint, store: ArtifactStore, target: Path) -> BundleInspection:
    """Export a deterministic owner-only bundle without overwriting an existing file."""
    CheckpointEngine(store).validate(checkpoint)
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"bundle target already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary_name = tempfile.mkstemp(prefix="dovet-bundle-", dir=target.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w", allowZip64=False) as archive:
            checkpoint_bytes = canonical_json(checkpoint.model_dump(mode="json"))
            info, data = _archive_entry("checkpoint.json", checkpoint_bytes)
            archive.writestr(info, data)
            handoff = CheckpointEngine.render_handoff(checkpoint).encode()
            info, data = _archive_entry("handoff.md", handoff)
            archive.writestr(info, data)
            digests = sorted(
                {file.sha256 for file in checkpoint.manifest.files if file.sha256 is not None}
            )
            for digest in digests:
                info, data = _archive_entry(f"objects/{digest}", store.read_bytes(digest))
                archive.writestr(info, data)
        os.chmod(temporary, 0o600)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        if temporary.stat().st_size > MAX_BUNDLE_BYTES:
            raise InvalidCheckpointBundle("bundle exceeds the size limit")
        os.link(temporary, target)
        directory = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return inspect_bundle(target)
    finally:
        temporary.unlink(missing_ok=True)


def _safe_members(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    infos = archive.infolist()
    if not infos or len(infos) > MAX_MEMBERS:
        raise InvalidCheckpointBundle("bundle has an invalid member count")
    members: dict[str, zipfile.ZipInfo] = {}
    total = 0
    for info in infos:
        name = info.filename
        path = PurePosixPath(name)
        if (
            name in members
            or info.flag_bits & 0x1
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
            or info.is_dir()
        ):
            raise InvalidCheckpointBundle(f"unsafe bundle member: {name}")
        unix_mode = info.external_attr >> 16
        file_type = stat.S_IFMT(unix_mode)
        if file_type not in (0, stat.S_IFREG):
            raise InvalidCheckpointBundle(f"non-file bundle member: {name}")
        total += info.file_size
        if info.file_size > MAX_BUNDLE_BYTES or total > MAX_BUNDLE_BYTES:
            raise InvalidCheckpointBundle("bundle expands beyond the size limit")
        members[name] = info
    return members


def inspect_bundle(path: Path) -> BundleInspection:
    """Validate all metadata and object bytes without mutating the local artifact store."""
    if path.is_symlink() or not path.is_file():
        raise InvalidCheckpointBundle("bundle must be a regular file")
    bundle_bytes = path.read_bytes()
    if len(bundle_bytes) > MAX_BUNDLE_BYTES:
        raise InvalidCheckpointBundle("bundle exceeds the size limit")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            members = _safe_members(archive)
            for required in ("checkpoint.json", "handoff.md"):
                if required not in members or members[required].file_size > MAX_METADATA_BYTES:
                    raise InvalidCheckpointBundle(f"bundle lacks valid {required}")
            try:
                checkpoint = Checkpoint.model_validate_json(archive.read("checkpoint.json"))
            except (ValidationError, UnicodeDecodeError) as error:
                raise InvalidCheckpointBundle("checkpoint metadata is invalid") from error
            if checkpoint.completeness != "ready":
                raise InvalidCheckpointBundle("checkpoint is not ready")
            manifest_digest = digest_json(checkpoint.manifest.model_dump(mode="json"))
            if manifest_digest != checkpoint.snapshot_sha256:
                raise InvalidCheckpointBundle("checkpoint snapshot digest does not match")
            expected_handoff = CheckpointEngine.render_handoff(checkpoint).encode()
            if archive.read("handoff.md") != expected_handoff:
                raise InvalidCheckpointBundle("handoff text does not match checkpoint data")
            expected_objects: dict[str, int] = {}
            for file in checkpoint.manifest.files:
                if CheckpointEngine.omission_reason(file.path) is not None:
                    raise InvalidCheckpointBundle(
                        f"checkpoint contains a prohibited path: {file.path}"
                    )
                if file.operation != "delete":
                    if file.sha256 is None:
                        raise InvalidCheckpointBundle(
                            f"checkpoint object is missing for {file.path}"
                        )
                    existing_size = expected_objects.setdefault(file.sha256, file.size_bytes)
                    if existing_size != file.size_bytes:
                        raise InvalidCheckpointBundle(
                            "one object is declared with conflicting sizes"
                        )
            expected_names = {"checkpoint.json", "handoff.md"} | {
                f"objects/{digest}" for digest in expected_objects
            }
            if set(members) != expected_names:
                raise InvalidCheckpointBundle("bundle contains missing or unexpected members")
            for digest, expected_size in expected_objects.items():
                data = archive.read(f"objects/{digest}")
                if len(data) != expected_size or sha256_bytes(data) != digest:
                    raise InvalidCheckpointBundle(f"checkpoint object failed integrity: {digest}")
    except (zipfile.BadZipFile, OSError) as error:
        raise InvalidCheckpointBundle("bundle archive is unreadable") from error
    return BundleInspection(
        checkpoint=checkpoint,
        bundle_sha256=sha256_bytes(bundle_bytes),
        object_count=len(expected_objects),
        total_object_bytes=sum(expected_objects.values()),
    )


def import_bundle(path: Path, store: ArtifactStore) -> BundleInspection:
    """Validate the complete archive first, then import immutable objects idempotently."""
    inspection = inspect_bundle(path)
    with zipfile.ZipFile(path, "r") as archive:
        object_digests = {
            file.sha256
            for file in inspection.checkpoint.manifest.files
            if file.sha256 is not None
        }
        for digest in sorted(object_digests):
            artifact = store.put_bytes(archive.read(f"objects/{digest}"))
            if artifact.sha256 != digest:
                raise InvalidCheckpointBundle("imported object digest changed")
    CheckpointEngine(store).validate(inspection.checkpoint)
    return inspection
