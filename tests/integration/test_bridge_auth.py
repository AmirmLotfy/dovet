from __future__ import annotations

from pathlib import Path

from dovet.api import SessionState, create_app, ensure_bridge_token
from fastapi.testclient import TestClient


def test_owner_only_bridge_can_issue_one_use_pairing_url(tmp_path: Path) -> None:
    token = ensure_bridge_token(tmp_path)
    assert (tmp_path / "bridge-token").stat().st_mode & 0o777 == 0o600
    sessions = SessionState()
    sessions.set_bridge_token(token)
    client = TestClient(create_app(state=sessions), base_url="http://127.0.0.1:4317")
    denied = client.post("/api/v1/session/issue")
    assert denied.status_code == 401
    issued = client.post("/api/v1/session/issue", headers={"X-Dovet-Bridge": token})
    assert issued.status_code == 200
    assert issued.json()["url"].startswith("http://127.0.0.1:4317/#pair=")
    nonce = issued.json()["url"].split("#pair=", 1)[1]
    paired = client.post("/api/v1/session/pair", json={"nonce": nonce})
    assert paired.status_code == 200
    replayed = client.post("/api/v1/session/pair", json={"nonce": nonce})
    assert replayed.status_code == 401
