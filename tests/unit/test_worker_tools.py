from __future__ import annotations

import sys
from pathlib import Path

import pytest
from dovet.canonical import sha256_bytes
from dovet_worker.agent import build_worker
from dovet_worker.tools import RestrictedTools, WorkerScope


def test_patch_is_hash_bound_and_scope_bound(tmp_path: Path) -> None:
    target = tmp_path / "allowed.py"
    target.write_text("value = 1\n", encoding="utf-8")
    tools = RestrictedTools(WorkerScope("token", tmp_path, frozenset({"allowed.py"}), 4))
    changed = tools.apply_patch(
        "token",
        "allowed.py",
        sha256_bytes(target.read_bytes()),
        "--- a/allowed.py\n+++ b/allowed.py\n@@ -1 +1 @@\n-value = 1\n+value = 2\n",
    )
    assert target.read_text(encoding="utf-8") == "value = 2\n"
    assert changed == sha256_bytes(target.read_bytes())
    with pytest.raises(PermissionError):
        tools.create_file("token", "protected_test.py", "pass\n")


def test_stale_lease_denies_every_tool(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("safe", encoding="utf-8")
    tools = RestrictedTools(
        WorkerScope("token", tmp_path, frozenset({"file.txt"}), 2),
        current_lease_generation=lambda: 3,
    )
    with pytest.raises(PermissionError, match="lease changed"):
        tools.read_file("token", "file.txt")


def test_only_approved_argv_can_run(tmp_path: Path) -> None:
    scope = WorkerScope(
        "token",
        tmp_path,
        frozenset(),
        1,
        approved_commands=(("probe", (sys.executable, "-c", "print('checked')")),),
    )
    tools = RestrictedTools(scope)
    result = tools.run_check("token", "probe")
    assert result.exit_code == 0
    assert result.output == "checked\n"
    with pytest.raises(PermissionError, match="not approved"):
        tools.run_check("token", "arbitrary")


def test_capability_token_is_not_exposed_to_model_tool_schemas(tmp_path: Path) -> None:
    secret = "never-send-this-token-to-the-model"  # noqa: S105 -- inert test sentinel
    tools = RestrictedTools(WorkerScope(secret, tmp_path, frozenset(), 1))
    agent = build_worker(
        model_id="amazon.nova-micro-v1:0",
        region="us-east-1",
        restricted=tools,
    )

    specs = agent.tool_registry.get_all_tool_specs()
    assert "scope_token" not in repr(specs)
    assert secret not in repr(specs)
