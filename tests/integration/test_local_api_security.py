from __future__ import annotations

from dovet.api import SessionState, create_app
from fastapi.testclient import TestClient


def test_host_origin_pairing_and_csrf() -> None:
    state = SessionState()
    nonce = state.issue_pairing_nonce()
    client = TestClient(create_app(state=state), base_url="http://127.0.0.1:4317")
    paired = client.post(
        "/api/v1/session/pair",
        json={"nonce": nonce},
        headers={"origin": "http://127.0.0.1:4317"},
    )
    assert paired.status_code == 200
    csrf = paired.json()["csrf_token"]
    assert client.get("/api/v1/status").status_code == 200
    assert client.post("/api/v1/runs/run_1/pause").status_code == 403
    unavailable = client.post(
        "/api/v1/runs/run_1/pause", headers={"x-dovet-csrf": csrf}
    )
    assert unavailable.status_code == 503
    assert "no interruption was attempted" in unavailable.json()["detail"]
    assert TestClient(create_app(), base_url="http://evil.test").get("/health").status_code == 400
