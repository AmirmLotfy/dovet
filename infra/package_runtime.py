"""Build an AgentCore direct-code ZIP with Linux arm64 dependencies."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "dovet-agentcore-runtime.zip"


def main() -> int:
    private_root = ROOT / "artifacts" / "private"
    private_root.mkdir(parents=True, exist_ok=True)
    build = Path(tempfile.mkdtemp(prefix="agentcore-package-", dir=private_root))
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required to package the AgentCore runtime")
    subprocess.run(  # noqa: S603
        [
            uv,
            "pip",
            "install",
            "--target",
            str(build),
            "--python-platform",
            "aarch64-manylinux2014",
            "--python-version",
            "3.12",
            "--only-binary",
            ":all:",
            "bedrock-agentcore==1.23.0",
            "boto3==1.43.93",
            "pydantic==2.13.5",
            "strands-agents==1.55.1",
        ],
        cwd=ROOT,
        check=True,
    )
    for source, target in (
        (ROOT / "services" / "daemon" / "src" / "dovet", build / "dovet"),
        (
            ROOT / "services" / "supervisor" / "src" / "dovet_supervisor",
            build / "dovet_supervisor",
        ),
    ):
        shutil.copytree(source, target, dirs_exist_ok=True)
    shutil.copy2(ROOT / "infra" / "runtime_main.py", build / "main.py")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(build.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(build))
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
