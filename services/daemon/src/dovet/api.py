"""Authenticated loopback API for the local console and MCP bridge."""

from __future__ import annotations

import hashlib
import os
import secrets
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from fastapi import Cookie, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from . import __version__
from .canonical import digest_json
from .models import Capability, HealthResponse, UsageAdviceView, UsageResponse, UsageWindowView
from .usage import CodexUsageReader, preservation_advice

ALLOWED_HOSTS = {"127.0.0.1:4317", "localhost:4317"}
ALLOWED_ORIGINS = {"http://127.0.0.1:4317", "http://localhost:4317"}


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PairRequest(StrictRequest):
    nonce: str = Field(min_length=32, max_length=256)


@dataclass
class SessionState:
    pairing_hash: str = field(
        default_factory=lambda: hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    )
    pairing_expires_at: float = 0
    sessions: dict[str, tuple[float, str]] = field(default_factory=dict)
    bridge_hash: str | None = None

    def set_bridge_token(self, token: str) -> None:
        self.bridge_hash = hashlib.sha256(token.encode()).hexdigest()

    def issue_pairing_nonce(self) -> str:
        nonce = secrets.token_urlsafe(32)
        self.pairing_hash = hashlib.sha256(nonce.encode()).hexdigest()
        self.pairing_expires_at = time.monotonic() + 120
        return nonce

    def exchange(self, nonce: str) -> tuple[str, str]:
        supplied = hashlib.sha256(nonce.encode()).hexdigest()
        if time.monotonic() > self.pairing_expires_at or not secrets.compare_digest(
            supplied, self.pairing_hash
        ):
            raise ValueError("pairing nonce is invalid or expired")
        self.pairing_expires_at = 0
        self.pairing_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        session = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        self.sessions[hashlib.sha256(session.encode()).hexdigest()] = (
            time.monotonic() + 8 * 60 * 60,
            csrf,
        )
        return session, csrf

    def verify(
        self,
        session: str | None,
        csrf: str | None,
        *,
        mutation: bool,
        bridge_token: str | None = None,
    ) -> None:
        if bridge_token is not None and self.bridge_hash is not None:
            supplied = hashlib.sha256(bridge_token.encode()).hexdigest()
            if secrets.compare_digest(supplied, self.bridge_hash):
                return
        if session is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "local session required")
        key = hashlib.sha256(session.encode()).hexdigest()
        record = self.sessions.get(key)
        if record is None or time.monotonic() > record[0]:
            self.sessions.pop(key, None)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "local session expired")
        if mutation and (csrf is None or not secrets.compare_digest(csrf, record[1])):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "CSRF token required")


def ensure_bridge_token(data_root: Path) -> str:
    """Load or create the owner-only bridge credential without printing it."""
    data_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    token_path = data_root / "bridge-token"
    try:
        token = token_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        token = secrets.token_urlsafe(48)
        descriptor = os.open(token_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(token + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    os.chmod(token_path, 0o600)
    if len(token) < 32:
        raise RuntimeError("local bridge credential is invalid")
    return token


def create_app(
    *, state: SessionState | None = None, console_dir: Path | None = None
) -> FastAPI:
    sessions = state or SessionState()
    app = FastAPI(title="Dovet local API", version=__version__, docs_url=None, redoc_url=None)
    app.state.sessions = sessions
    app.add_middleware(
        CORSMiddleware,
        allow_origins=sorted(ALLOWED_ORIGINS),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-Dovet-CSRF"],
    )

    @app.middleware("http")
    async def protect_loopback(request: Request, call_next):  # type: ignore[no-untyped-def]
        host = request.headers.get("host")
        if host not in ALLOWED_HOSTS:
            return Response("invalid host", status_code=400)
        origin = request.headers.get("origin")
        if origin is not None and origin not in ALLOWED_ORIGINS:
            return Response("invalid origin", status_code=403)
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        capabilities = [
            Capability(name="local_ledger", status="ready", detail="SQLite and local artifacts"),
            Capability(
                name="codex_usage",
                status="ready",
                detail="supported app-server read; missing or stale values remain unknown",
            ),
            Capability(
                name="codex_managed",
                status="ready",
                detail="owned start, interruption and checkpoint verified",
            ),
            Capability(
                name="bedrock",
                status="blocked",
                detail="authenticated discovery passes; invocation is not allowed",
            ),
        ]
        return HealthResponse(
            version=__version__,
            readiness="degraded",
            capability_digest=digest_json([item.model_dump() for item in capabilities]),
            capabilities=capabilities,
        )

    @app.post("/api/v1/session/pair")
    async def pair(payload: PairRequest, response: Response) -> dict[str, str]:
        try:
            session, csrf = sessions.exchange(payload.nonce)
        except ValueError as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(error)) from error
        response.set_cookie(
            "dovet_session",
            session,
            httponly=True,
            secure=False,
            samesite="strict",
            max_age=8 * 60 * 60,
            path="/",
        )
        return {"csrf_token": csrf, "status": "paired"}

    @app.post("/api/v1/session/issue")
    async def issue_pairing(
        x_dovet_bridge: str | None = Header(default=None),
    ) -> dict[str, str]:
        sessions.verify(None, None, mutation=True, bridge_token=x_dovet_bridge)
        nonce = sessions.issue_pairing_nonce()
        return {"url": f"http://127.0.0.1:4317/#pair={nonce}", "expires_in": "120s"}

    @app.get("/api/v1/status")
    async def local_status(
        dovet_session: str | None = Cookie(default=None),
        x_dovet_bridge: str | None = Header(default=None),
    ) -> dict[str, object]:
        sessions.verify(
            dovet_session, None, mutation=False, bridge_token=x_dovet_bridge
        )
        return {
            "service": "connected",
            "work": [],
            "needs_you": [],
            "history": [],
            "message": (
                "No protected work yet. Start a managed task or connect a project "
                "in observation mode."
            ),
        }

    @app.get("/api/v1/connections/codex/usage", response_model=UsageResponse)
    def codex_usage(
        dovet_session: str | None = Cookie(default=None),
        x_dovet_bridge: str | None = Header(default=None),
    ) -> UsageResponse:
        sessions.verify(
            dovet_session, None, mutation=False, bridge_token=x_dovet_bridge
        )
        snapshot = CodexUsageReader().read()
        advice = preservation_advice(snapshot)
        return UsageResponse(
            observed_at=snapshot.observed_at,
            state=snapshot.state.value,
            windows=[UsageWindowView(**asdict(window)) for window in snapshot.windows],
            source="codex-app-server",
            error=snapshot.error,
            advice=UsageAdviceView(**asdict(advice)),
        )

    @app.post("/api/v1/runs/{run_id}/pause")
    async def pause_run(
        run_id: str,
        dovet_session: str | None = Cookie(default=None),
        x_dovet_csrf: str | None = Header(default=None),
        x_dovet_bridge: str | None = Header(default=None),
    ) -> None:
        sessions.verify(
            dovet_session,
            x_dovet_csrf,
            mutation=True,
            bridge_token=x_dovet_bridge,
        )
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Pause for {run_id} is unavailable until its managed-worker ownership "
                "record is loaded; no interruption was attempted."
            ),
        )

    if console_dir is not None and (console_dir / "index.html").is_file():
        app.mount("/", StaticFiles(directory=console_dir, html=True), name="console")

    return app


app = create_app()
