"""Dovet command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .database import Ledger
from .doctor import doctor_json


def _data_root() -> Path:
    return Path.home() / "Library" / "Application Support" / "Dovet"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dovet")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="read-only capability report")
    commands.add_parser("init-state", help="initialize the local SQLite ledger")
    serve = commands.add_parser("serve", help="run the loopback daemon in the foreground")
    serve.add_argument("--host", default="127.0.0.1", choices=("127.0.0.1",))
    serve.add_argument("--port", default=4317, type=int)
    serve.add_argument("--pair", action="store_true", help="print a one-use console URL")
    service = commands.add_parser("service", help="manage the independent local service")
    service.add_argument("action", choices=("install", "start", "stop", "status", "uninstall"))
    status = commands.add_parser("status", help="show local readiness")
    status.add_argument("--json", action="store_true")
    usage = commands.add_parser("usage", help="read supported Codex usage without auth-file access")
    usage.add_argument("--json", action="store_true")
    bundle = commands.add_parser("bundle", help="verify or restore a portable checkpoint bundle")
    bundle.add_argument("action", choices=("verify", "restore"))
    bundle.add_argument("path", type=Path)
    bundle.add_argument("--to", type=Path, help="new destination directory for restore")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "doctor":
        print(doctor_json())
        return 0
    if args.command == "init-state":
        root = _data_root()
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        Ledger(root / "state.sqlite3").migrate()
        print("Dovet state initialized")
        return 0
    if args.command == "status":
        status_result = {
            "version": __version__,
            "state": "ready" if (_data_root() / "state.sqlite3").exists() else "not_initialized",
        }
        print(
            json.dumps(status_result)
            if args.json
            else f"Dovet {status_result['version']}: {status_result['state']}"
        )
        return 0
    if args.command == "usage":
        from .usage import CodexUsageReader, preservation_advice

        snapshot = CodexUsageReader().read()
        advice = preservation_advice(snapshot)
        usage_result = snapshot.public_dict()
        usage_result["advice"] = asdict(advice)
        if args.json:
            print(json.dumps(usage_result, indent=2, default=str))
        else:
            print(f"Codex usage: {snapshot.state.value}; preservation: {advice.level.value}")
        return 0
    if args.command == "bundle":
        from .artifacts import ArtifactStore
        from .bundles import import_bundle, inspect_bundle
        from .checkpoints import CheckpointEngine

        if args.action == "verify":
            inspection = inspect_bundle(args.path)
        else:
            if args.to is None:
                raise SystemExit("bundle restore requires --to")
            if args.to.is_symlink():
                raise SystemExit("restore destination must not be a symlink")
            if args.to.exists() and not args.to.is_dir():
                raise SystemExit("restore destination must be a directory")
            if args.to.exists() and any(args.to.iterdir()):
                raise SystemExit("restore destination must be absent or empty")
            store = ArtifactStore(_data_root() / "artifacts")
            inspection = import_bundle(args.path, store)
            CheckpointEngine(store).restore(inspection.checkpoint, args.to)
        print(
            json.dumps(
                {
                    "status": "verified" if args.action == "verify" else "restored",
                    "checkpoint_id": inspection.checkpoint.id,
                    "snapshot_sha256": inspection.checkpoint.snapshot_sha256,
                    "bundle_sha256": inspection.bundle_sha256,
                    "object_count": inspection.object_count,
                },
                indent=2,
            )
        )
        return 0
    if args.command == "serve":
        import uvicorn

        from .api import SessionState, create_app, ensure_bridge_token
        from .evidence import RunEvidenceStore

        state = SessionState()
        state.set_bridge_token(ensure_bridge_token(_data_root()))
        checkout_console = Path(__file__).resolve().parents[4] / "apps" / "console" / "dist"
        local_app = create_app(
            state=state,
            console_dir=checkout_console,
            evidence_store=RunEvidenceStore(_data_root() / "receipts"),
        )
        if args.pair:
            nonce = state.issue_pairing_nonce()
            print(f"http://{args.host}:{args.port}/#pair={nonce}")
        uvicorn.run(local_app, host=args.host, port=args.port, log_level="info")
        return 0
    if args.command == "service":
        from .service import service_command

        return service_command(args.action)
    return 2


if __name__ == "__main__":
    sys.exit(main())
