"""Create a source archive from the exact committed and tagged Dovet tree."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
TAG_PATTERN = re.compile(r"v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def command(*argv: str) -> str:
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"release command failed: {argv[0]}: {detail}")
    return result.stdout.strip()


def main() -> int:
    commit = command("git", "rev-parse", "HEAD")
    if command("git", "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("release packaging requires a clean committed tracked tree")
    tag = os.environ.get("DOVET_RELEASE_TAG", "v0.1.3")
    if not TAG_PATTERN.fullmatch(tag):
        raise RuntimeError("DOVET_RELEASE_TAG must be a semantic version tag")
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
