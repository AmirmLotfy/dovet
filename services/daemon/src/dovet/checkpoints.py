"""Quiescent, content-addressed checkpoint capture and restoration."""

from __future__ import annotations

import os
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

from .artifacts import ArtifactStore
from .canonical import canonical_json, digest_json, sha256_bytes
from .models import Checkpoint, CheckpointManifest, ManifestFile
from .paths import reject_platform_collisions, resolve_beneath, validate_relative_path


class InconsistentSnapshotError(RuntimeError):
    pass


@dataclass(frozen=True)
class CaptureOutcome:
    """Result of a capture attempt without discarding the prior verified state."""

    captured: Checkpoint | None
    retained: Checkpoint | None
    error: str | None

    @property
    def active(self) -> Checkpoint | None:
        return self.captured or self.retained


class CheckpointEngine:
    EXCLUDED_DIRECTORIES = frozenset(
        {
            ".git",
            ".next",
            ".turbo",
            ".venv",
            "build",
            "dist",
            "node_modules",
            "target",
            "vendor",
        }
    )
    SENSITIVE_NAMES = frozenset(
        {
            ".npmrc",
            ".pypirc",
            "credentials",
            "credentials.json",
            "id_ed25519",
            "id_rsa",
        }
    )
    SENSITIVE_SUFFIXES = (".key", ".p12", ".pem", ".pfx")

    def __init__(self, store: ArtifactStore, *, maximum_file_bytes: int = 100_000_000) -> None:
        self.store = store
        if maximum_file_bytes < 1:
            raise ValueError("maximum file size must be positive")
        self.maximum_file_bytes = maximum_file_bytes

    @classmethod
    def omission_reason(cls, relative: str) -> str | None:
        parts = relative.split("/")
        if any(part in cls.EXCLUDED_DIRECTORIES for part in parts[:-1]):
            return "excluded dependency, build, or VCS directory"
        name = parts[-1].casefold()
        if (
            name.startswith(".env")
            or name in cls.SENSITIVE_NAMES
            or name.endswith(cls.SENSITIVE_SUFFIXES)
            or "credential" in name
            or "secret" in name
        ):
            return "credential-like filename"
        return None

    def capture(
        self,
        *,
        root: Path,
        paths: list[str],
        run_id: str,
        task_version: int,
        policy_sha256: str,
        base_commit: str,
    ) -> Checkpoint:
        clean_paths = sorted(validate_relative_path(path) for path in paths)
        if len(clean_paths) != len(set(clean_paths)):
            raise ValueError("duplicate checkpoint path")
        reject_platform_collisions(clean_paths)
        files: list[ManifestFile] = []
        omissions: list[str] = []
        for relative in clean_paths:
            reason = self.omission_reason(relative)
            if reason is not None:
                omissions.append(f"Omitted {relative}: {reason}")
                continue
            path = resolve_beneath(root, relative)
            if not path.is_file():
                raise ValueError(f"unsupported checkpoint entry: {relative}")
            before = path.stat()
            if before.st_size > self.maximum_file_bytes:
                omissions.append(f"Omitted {relative}: exceeds file-size limit")
                continue
            data = path.read_bytes()
            after = path.stat()
            if (before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
            ):
                raise InconsistentSnapshotError(f"file changed during capture: {relative}")
            artifact = self.store.put_bytes(data)
            files.append(
                ManifestFile(
                    path=relative,
                    operation="modify",
                    sha256=artifact.sha256,
                    size_bytes=artifact.size_bytes,
                    mode=before.st_mode & 0o777,
                )
            )
        for file in files:
            current = resolve_beneath(root, file.path).read_bytes()
            if len(current) != file.size_bytes or sha256_bytes(current) != file.sha256:
                raise InconsistentSnapshotError(f"file changed during capture: {file.path}")
        manifest = CheckpointManifest(
            run_id=run_id,
            task_version=task_version,
            policy_sha256=policy_sha256,
            base_commit=base_commit,
            files=files,
        )
        snapshot = digest_json(manifest.model_dump(mode="json"))
        checkpoint = Checkpoint(
            id=f"ck_{uuid.uuid4().hex}",
            manifest=manifest,
            snapshot_sha256=snapshot,
            completeness="ready",
            decisions=omissions,
        )
        self.store.put_bytes(canonical_json(checkpoint.model_dump(mode="json")))
        return checkpoint

    def capture_preserving(
        self,
        *,
        root: Path,
        paths: list[str],
        run_id: str,
        task_version: int,
        policy_sha256: str,
        base_commit: str,
        previous_ready: Checkpoint | None = None,
    ) -> CaptureOutcome:
        """Capture new state while retaining a previously validated checkpoint on failure."""
        if previous_ready is not None:
            self.validate(previous_ready)
            if previous_ready.completeness != "ready":
                raise ValueError("previous checkpoint is not ready")
        try:
            checkpoint = self.capture(
                root=root,
                paths=paths,
                run_id=run_id,
                task_version=task_version,
                policy_sha256=policy_sha256,
                base_commit=base_commit,
            )
        except (OSError, ValueError, InconsistentSnapshotError) as error:
            return CaptureOutcome(captured=None, retained=previous_ready, error=str(error))
        return CaptureOutcome(captured=checkpoint, retained=None, error=None)

    def validate(self, checkpoint: Checkpoint) -> None:
        if checkpoint.completeness != "ready":
            raise OSError("checkpoint is not ready")
        manifest_value = checkpoint.manifest.model_dump(mode="json")
        if digest_json(manifest_value) != checkpoint.snapshot_sha256:
            raise OSError("checkpoint manifest digest mismatch")
        for file in checkpoint.manifest.files:
            if file.operation == "delete":
                continue
            if file.sha256 is None:
                raise OSError(f"checkpoint blob missing for {file.path}")
            data = self.store.read_bytes(file.sha256)
            if len(data) != file.size_bytes or sha256_bytes(data) != file.sha256:
                raise OSError(f"checkpoint blob invalid for {file.path}")

    def latest_valid(self, checkpoints: list[Checkpoint]) -> Checkpoint | None:
        """Return the first valid ready checkpoint from newest to oldest."""
        for checkpoint in checkpoints:
            try:
                self.validate(checkpoint)
            except OSError:
                continue
            return checkpoint
        return None

    def restore(self, checkpoint: Checkpoint, destination: Path) -> None:
        self.validate(checkpoint)
        destination.mkdir(parents=True, exist_ok=True)
        for file in checkpoint.manifest.files:
            target = resolve_beneath(destination, file.path, allow_missing=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            if file.operation == "delete":
                target.unlink(missing_ok=True)
                continue
            if file.sha256 is None:
                raise OSError(f"checkpoint blob missing for {file.path}")
            data = self.store.read_bytes(file.sha256)
            if len(data) != file.size_bytes or sha256_bytes(data) != file.sha256:
                raise OSError(f"checkpoint blob invalid for {file.path}")
            descriptor, temporary = tempfile.mkstemp(prefix="restore-", dir=target.parent)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.chmod(temporary, file.mode)
                os.replace(temporary, target)
            finally:
                Path(temporary).unlink(missing_ok=True)

    @staticmethod
    def render_handoff(checkpoint: Checkpoint) -> str:
        lines = [
            "# Dovet recovery handoff",
            "",
            f"Checkpoint: `{checkpoint.id}`",
            f"Snapshot: `{checkpoint.snapshot_sha256}`",
            f"Task version: {checkpoint.manifest.task_version}",
            "",
            "## Captured files",
        ]
        lines.extend(
            f"- `{file.path}` — {file.operation}, `{file.sha256}`"
            for file in checkpoint.manifest.files
        )
        lines.extend(
            [
                "",
                "Statements here are derived from observable checkpoint data; "
                "they do not contain private model reasoning.",
            ]
        )
        return "\n".join(lines) + "\n"
