"""Create a source archive from the exact committed Dovet tree."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def command(*argv: str) -> str:
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        raise RuntimeError(f"release command failed: {argv[0]} {argv[1]}")
    return result.stdout.strip()


def main() -> int:
    commit = command("git", "rev-parse", "HEAD")
    if command("git", "status", "--porcelain"):
        raise RuntimeError("release packaging requires a clean committed tree")
    tag = "v0.1.0"
    tags = command("git", "tag", "--points-at", "HEAD").splitlines()
    if tag not in tags:
        raise RuntimeError(f"release commit must carry immutable tag {tag}")
    ARTIFACTS.mkdir(exist_ok=True)
    archive = ARTIFACTS / f"dovet-source-{commit[:12]}.tar.gz"
    command(
        "git",
        "archive",
        "--format=tar.gz",
        f"--prefix=dovet-{tag}/",
        f"--output={archive}",
        commit,
    )
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(f"{archive.relative_to(ROOT)} {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
