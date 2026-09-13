"""Build an honest, machine-readable Dovet release gate report."""

from __future__ import annotations

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx
from dovet.evidence import InvalidRunEvidence, RunEvidenceStore

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DATA_ROOT = Path.home() / "Library" / "Application Support" / "Dovet"
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "dist",
    "node_modules",
    "private-artifacts",
}
TEXT_SUFFIXES = {
    "",
    ".css",
    ".html",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}"),
}


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def git_commit() -> str | None:
    result = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )  # noqa: S603
    return result.stdout.strip() if result.returncode == 0 else None


def secret_scan() -> Check:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if "artifacts/private" in path.as_posix() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        if path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}:{label}")
    return Check(
        "secret_scan",
        "FAIL" if findings else "PASS",
        ", ".join(findings) if findings else "no credential patterns found in release text files",
    )


def test_report() -> Check:
    path = ARTIFACTS / "test-report-core.xml"
    if not path.exists():
        return Check("core_tests", "BLOCKED", "sanitized JUnit report is missing")
    suite = next(ET.parse(path).getroot().iter("testsuite"))  # noqa: S314
    total = int(suite.get("tests", "0"))
    failures = int(suite.get("failures", "0")) + int(suite.get("errors", "0"))
    return Check(
        "core_tests",
        "PASS" if total > 0 and failures == 0 else "FAIL",
        f"{total} tests, {failures} failures or errors",
    )


def public_page(name: str, url: str) -> Check:
    try:
        response = httpx.get(url, follow_redirects=True, timeout=12)
        is_dovet = response.status_code == 200 and "Dovet" in response.text
        detail = f"HTTP {response.status_code}; Dovet content {'present' if is_dovet else 'absent'}"
        return Check(name, "PASS" if is_dovet else "BLOCKED", detail)
    except httpx.HTTPError:
        return Check(name, "BLOCKED", "public URL could not be verified")


def bedrock_check() -> Check:
    try:
        evidence = RunEvidenceStore(DATA_ROOT / "receipts").read("vertical_run")
    except (FileNotFoundError, InvalidRunEvidence):
        evidence = None
    if evidence is not None:
        return Check(
            "live_strands_bedrock",
            "PASS",
            f"validated run {evidence.run_id}; model {evidence.model_id}",
        )
    path = ARTIFACTS / "aws-bedrock-probe.json"
    if not path.exists():
        return Check("live_strands_bedrock", "BLOCKED", "probe evidence is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    invocation = data.get("invocation", {})
    successful = invocation.get("successful_requests") if isinstance(invocation, dict) else None
    return Check(
        "live_strands_bedrock",
        "PASS" if isinstance(successful, int) and successful > 0 else "BLOCKED",
        f"successful provider requests: {successful if successful is not None else 'unknown'}",
    )


def video_check() -> Check:
    path = ROOT / "submission" / "video" / "dovet-demo.mp4"
    if not path.exists():
        return Check("final_video", "BLOCKED", "finished narrated MP4 is missing")
    result = subprocess.run(  # noqa: S603
        (
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        media = json.loads(result.stdout)
        duration = float(media["format"]["duration"])
        video = next(item for item in media["streams"] if item.get("codec_type") == "video")
        audio = next(item for item in media["streams"] if item.get("codec_type") == "audio")
        valid = (
            275 <= duration <= 290
            and video.get("codec_name") == "h264"
            and video.get("width") == 1920
            and video.get("height") == 1080
            and audio.get("codec_name") == "aac"
        )
    except (KeyError, StopIteration, TypeError, ValueError, json.JSONDecodeError):
        duration = 0
        valid = False
    return Check(
        "final_video",
        "PASS" if result.returncode == 0 and valid else "FAIL",
        f"duration {duration:.2f} seconds",
    )


def review_recordings() -> list[dict[str, object]]:
    path = ROOT / "private-artifacts" / "video" / "picture-edit-manifest.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        {
            "path": data.get("path"),
            "sha256": data.get("sha256"),
            "duration_seconds": data.get("duration_seconds"),
            "status": data.get("status"),
        }
    ]


def recording_preflight_check() -> Check:
    path = ARTIFACTS / "recording-preflight.json"
    if not path.exists():
        return Check("recording_preflight", "BLOCKED", "recording preflight is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    current = data.get("status")
    detail = data.get("detail")
    return Check(
        "recording_preflight",
        "PASS" if current == "PASS" else "BLOCKED",
        str(detail) if detail else "recording preflight has no detail",
    )


def install_smoke_check() -> Check:
    path = ARTIFACTS / "install-smoke.json"
    if not path.exists():
        return Check("isolated_install", "BLOCKED", "isolated install evidence is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    passed = (
        data.get("status") == "PASS"
        and data.get("packaged_schema_migration") == "PASS"
        and data.get("checkpoint_bundle_import") == "PASS"
    )
    return Check(
        "isolated_install",
        "PASS" if passed else "FAIL",
        (
            f"wheel {data.get('wheel', 'unknown')}; packaged schema "
            f"{data.get('packaged_schema_migration', 'unknown')}; bundle import "
            f"{data.get('checkpoint_bundle_import', 'unknown')}"
        ),
    )


def file_check(name: str, path: Path, minimum_bytes: int) -> Check:
    size = path.stat().st_size if path.exists() else 0
    return Check(name, "PASS" if size >= minimum_bytes else "FAIL", f"{size} bytes")


def main() -> int:
    commit = git_commit()
    checks = [
        file_check("apache_license", ROOT / "LICENSE", 10_000),
        file_check("python_lockfile", ROOT / "uv.lock", 1_000),
        file_check("node_lockfile", ROOT / "pnpm-lock.yaml", 1_000),
        secret_scan(),
        test_report(),
        install_smoke_check(),
        bedrock_check(),
        recording_preflight_check(),
        public_page("vercel_site", "https://dovet-site.vercel.app"),
        public_page("dovet_site", "https://dovet.site"),
        video_check(),
        Check(
            "release_commit",
            "PASS" if commit else "BLOCKED",
            commit or "repository has no commit",
        ),
        Check("public_source", "BLOCKED", "public repository and tagged release are not published"),
        Check("devpost_submission", "BLOCKED", "submission receipt is not available"),
    ]
    status = "PASS"
    if any(check.status == "FAIL" for check in checks):
        status = "FAIL"
    elif any(check.status == "BLOCKED" for check in checks):
        status = "BLOCKED"
    report = {
        "schema_version": "1",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": status,
        "commit_sha": commit,
        "checks": [asdict(check) for check in checks],
        "deployed_urls": {
            "vercel_production": "https://dovet-site.vercel.app",
            "intended_domain": "https://dovet.site",
        },
        "recordings": review_recordings(),
        "test_reports": ["artifacts/test-report-core.xml"],
        "unresolved_items": [check.name for check in checks if check.status != "PASS"],
        "public_submission_links": {},
    }
    ARTIFACTS.mkdir(exist_ok=True)
    output = ARTIFACTS / "release-evidence.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "report": str(output.relative_to(ROOT))}))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
