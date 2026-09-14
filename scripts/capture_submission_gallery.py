"""Capture submission-ready screenshots from the real local daemon and public site."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path.home() / "Library" / "Application Support" / "Dovet"
OUTPUT = ROOT / "submission" / "screenshots" / "gallery"
MANIFEST = OUTPUT / "manifest.json"

CAPTURES = {
    "01-console-work-real.png": (
        1800,
        1200,
        "actual loopback console paired to independent daemon",
    ),
    "02-console-connections-real.png": (1800, 1200, "actual daemon capability response"),
    "03-public-home-real.png": (1800, 1200, "deployed public home page"),
    "04-public-evidence-real.png": (1800, 1200, "deployed public evidence section"),
    "05-product-receipt-fixture-disclosed.png": (
        1800,
        1200,
        "deployed deterministic UI fixture with visible disclosure",
    ),
    "06-managed-interruption-evidence-real.png": (
        1800,
        1200,
        "deployed judge page backed by the observed managed interruption artifact",
    ),
    "07-architecture-page-real.png": (1800, 1200, "deployed architecture evidence page"),
    "08-provider-blocker-real.png": (1800, 1200, "deployed provider blocker disclosure"),
    "09-security-boundaries-real.png": (1800, 1200, "deployed security documentation"),
    "10-public-repository-real.png": (1800, 1200, "anonymous public GitHub repository"),
    "11-public-release-real.png": (1800, 1200, "anonymous public v0.1.6 release"),
    "12-hosted-ci-pass-real.png": (1800, 1200, "anonymous hosted CI run"),
    "13-public-home-mobile-real.png": (1200, 1800, "deployed public home page at narrow width"),
}


def pair_nonce() -> str:
    token = (DATA_ROOT / "bridge-token").read_text(encoding="utf-8").strip()
    if len(token) < 32:
        raise RuntimeError("local bridge credential is invalid")
    deadline = time.monotonic() + 15
    while True:
        try:
            response = httpx.post(
                "http://127.0.0.1:4317/api/v1/session/issue",
                headers={"X-Dovet-Bridge": token},
                timeout=2,
            )
            response.raise_for_status()
            value = response.json().get("url")
            if isinstance(value, str) and value.startswith("http://127.0.0.1:4317/#pair="):
                return value.split("#pair=", 1)[1]
            raise RuntimeError("local service returned an invalid pairing response")
        except httpx.HTTPError:
            if time.monotonic() >= deadline:
                raise RuntimeError("local service did not become ready") from None
            time.sleep(0.2)


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"{path.name} is not a PNG")
    return struct.unpack(">II", header[16:24])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(
        {
            "DOVET_CAPTURE_SUBMISSION_GALLERY": "approved",
            "DOVET_GALLERY_OUTPUT_DIR": str(OUTPUT),
            "DOVET_GALLERY_SITE_URL": "https://dovet.site",
            "DOVET_PAIR_NONCE": pair_nonce(),
            "DOVET_RECORD_BASE_URL": "http://127.0.0.1:4317",
        }
    )
    completed = subprocess.run(  # noqa: S603
        (
            "pnpm",
            "--filter",
            "@dovet/console",
            "exec",
            "playwright",
            "test",
            "tests/capture-submission-gallery.spec.ts",
            "--project=desktop",
        ),
        cwd=ROOT,
        env=environment,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Playwright failed with exit {completed.returncode}")

    evidence = []
    for name, (width, height, provenance) in CAPTURES.items():
        path = OUTPUT / name
        if not path.is_file():
            raise RuntimeError(f"missing capture: {name}")
        if png_size(path) != (width, height):
            raise RuntimeError(f"unexpected dimensions for {name}: {png_size(path)}")
        if path.stat().st_size > 5 * 1024 * 1024:
            raise RuntimeError(f"capture exceeds Devpost's 5 MB limit: {name}")
        evidence.append(
            {
                "file": name,
                "width": width,
                "height": height,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "provenance": provenance,
            }
        )

    MANIFEST.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "captured_at": datetime.now(UTC).isoformat(),
                "release": "v0.1.6",
                "public_site": "https://dovet.site",
                "repository": "https://github.com/AmirmLotfy/dovet",
                "limitations": [
                    "The product receipt image is a deterministic contract fixture and is "
                    "disclosed in the filename and page caption.",
                    "The live Strands/Bedrock recovery remains blocked and no screenshot "
                    "claims otherwise.",
                ],
                "captures": evidence,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "captures": len(evidence), "manifest": str(MANIFEST)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
