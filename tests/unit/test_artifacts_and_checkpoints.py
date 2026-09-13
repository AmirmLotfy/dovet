from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from dovet.artifacts import ArtifactStore
from dovet.bundles import InvalidCheckpointBundle, export_bundle, import_bundle, inspect_bundle
from dovet.canonical import canonical_json, digest_json, sha256_bytes
from dovet.checkpoints import CheckpointEngine
from dovet.models import Checkpoint, CheckpointManifest, ManifestFile


def test_checkpoint_roundtrip_is_binary_safe(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "restored"
    source.mkdir()
    (source / "text.txt").write_text("hello \u2603", encoding="utf-8")
    (source / "binary.bin").write_bytes(bytes(range(256)))
    engine = CheckpointEngine(ArtifactStore(tmp_path / "store"))
    checkpoint = engine.capture(
        root=source,
        paths=["text.txt", "binary.bin"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    engine.restore(checkpoint, destination)
    assert (destination / "text.txt").read_bytes() == (source / "text.txt").read_bytes()
    assert (destination / "binary.bin").read_bytes() == bytes(range(256))


def test_corrupt_object_is_rejected(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "store")
    artifact = store.put_bytes(b"trusted")
    artifact.path.write_bytes(b"changed")
    with pytest.raises(OSError, match="integrity"):
        store.read_bytes(artifact.sha256)


def test_original_source_is_not_modified_by_restore(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("source")
    engine = CheckpointEngine(ArtifactStore(tmp_path / "store"))
    checkpoint = engine.capture(
        root=source,
        paths=["a.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    destination = tmp_path / "recovery"
    engine.restore(checkpoint, destination)
    (destination / "a.txt").write_text("replacement")
    assert (source / "a.txt").read_text() == "source"


def test_checkpoint_omits_credentials_build_outputs_and_large_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / ".env.local").write_text("TOKEN=private")
    (source / "node_modules").mkdir()
    (source / "node_modules" / "dependency.js").write_text("generated")
    (source / "large.bin").write_bytes(b"x" * 21)
    (source / "safe.py").write_text("print('safe')")
    engine = CheckpointEngine(ArtifactStore(tmp_path / "store"), maximum_file_bytes=20)
    checkpoint = engine.capture(
        root=source,
        paths=[".env.local", "node_modules/dependency.js", "large.bin", "safe.py"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    assert [file.path for file in checkpoint.manifest.files] == ["safe.py"]
    assert checkpoint.decisions == [
        "Omitted .env.local: credential-like filename",
        "Omitted large.bin: exceeds file-size limit",
        "Omitted node_modules/dependency.js: excluded dependency, build, or VCS directory",
    ]
    artifact_bytes = b"".join(
        path.read_bytes() for path in (tmp_path / "store" / "objects").rglob("*") if path.is_file()
    )
    assert b"TOKEN=private" not in artifact_bytes


def test_failed_capture_retains_previous_verified_checkpoint(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    path = source / "work.txt"
    path.write_text("verified")
    engine = CheckpointEngine(ArtifactStore(tmp_path / "store"))
    previous = engine.capture(
        root=source,
        paths=["work.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    path.unlink()
    outcome = engine.capture_preserving(
        previous_ready=previous,
        root=source,
        paths=["work.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    assert outcome.captured is None
    assert outcome.active == previous
    assert outcome.error is not None


def test_corrupt_newest_checkpoint_falls_back_to_older_valid_one(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    path = source / "work.txt"
    store = ArtifactStore(tmp_path / "store")
    engine = CheckpointEngine(store)
    path.write_text("old")
    older = engine.capture(
        root=source,
        paths=["work.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    path.write_text("new")
    newest = engine.capture(
        root=source,
        paths=["work.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    newest_digest = newest.manifest.files[0].sha256
    assert newest_digest is not None
    store.object_path(newest_digest).write_bytes(b"corrupt")
    assert engine.latest_valid([newest, older]) == older


def test_portable_bundle_is_deterministic_and_restores_after_import(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "work.txt").write_text("portable\n", encoding="utf-8")
    source_store = ArtifactStore(tmp_path / "source-store")
    checkpoint = CheckpointEngine(source_store).capture(
        root=source,
        paths=["work.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    first = export_bundle(checkpoint, source_store, tmp_path / "first.dovet")
    second = export_bundle(checkpoint, source_store, tmp_path / "second.dovet")
    assert first.bundle_sha256 == second.bundle_sha256
    assert first.object_count == 1

    target_store = ArtifactStore(tmp_path / "target-store")
    imported = import_bundle(tmp_path / "first.dovet", target_store)
    restored = tmp_path / "restored"
    CheckpointEngine(target_store).restore(imported.checkpoint, restored)
    assert (restored / "work.txt").read_text(encoding="utf-8") == "portable\n"


def test_bundle_rejects_duplicate_or_unexpected_members(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "work.txt").write_text("trusted", encoding="utf-8")
    store = ArtifactStore(tmp_path / "store")
    checkpoint = CheckpointEngine(store).capture(
        root=source,
        paths=["work.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    bundle = tmp_path / "checkpoint.dovet"
    export_bundle(checkpoint, store, bundle)
    with zipfile.ZipFile(bundle, "a") as archive:
        archive.writestr("../outside", b"untrusted")
    with pytest.raises(InvalidCheckpointBundle, match="unsafe bundle member"):
        inspect_bundle(bundle)


def test_bundle_rejects_corrupt_object_before_import(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "work.txt").write_text("trusted", encoding="utf-8")
    store = ArtifactStore(tmp_path / "store")
    checkpoint = CheckpointEngine(store).capture(
        root=source,
        paths=["work.txt"],
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
    )
    clean = tmp_path / "clean.dovet"
    export_bundle(checkpoint, store, clean)
    corrupt = tmp_path / "corrupt.dovet"
    digest = checkpoint.manifest.files[0].sha256
    assert digest is not None
    with zipfile.ZipFile(clean, "r") as source_archive, zipfile.ZipFile(corrupt, "w") as target:
        for info in source_archive.infolist():
            data = b"changed" if info.filename == f"objects/{digest}" else source_archive.read(info)
            target.writestr(info, data)
    target_store = ArtifactStore(tmp_path / "target")
    with pytest.raises(InvalidCheckpointBundle, match="failed integrity"):
        import_bundle(corrupt, target_store)
    assert not any(target_store.objects.rglob(digest))


def test_bundle_rejects_credential_like_manifest_path(tmp_path: Path) -> None:
    data = b"TOKEN=private"
    digest = sha256_bytes(data)
    manifest = CheckpointManifest(
        run_id="run_1",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="b" * 40,
        files=[
            ManifestFile(
                path=".env",
                operation="modify",
                sha256=digest,
                size_bytes=len(data),
                mode=0o600,
            )
        ],
    )
    checkpoint = Checkpoint(
        id="ck_untrusted",
        manifest=manifest,
        snapshot_sha256=digest_json(manifest.model_dump(mode="json")),
        completeness="ready",
    )
    bundle = tmp_path / "untrusted.dovet"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("checkpoint.json", canonical_json(checkpoint.model_dump(mode="json")))
        archive.writestr("handoff.md", CheckpointEngine.render_handoff(checkpoint))
        archive.writestr(f"objects/{digest}", data)
    with pytest.raises(InvalidCheckpointBundle, match="prohibited path"):
        inspect_bundle(bundle)
